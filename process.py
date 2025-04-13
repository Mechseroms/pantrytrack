import database, MyDataclasses, psycopg2, datetime,json
from config import config

def dropSiteTables(conn, site_manager: MyDataclasses.SiteManager):
    try:
        for table in site_manager.drop_order:
            database.__dropTable(conn, site_manager.site_name, table)
            with open("process.log", "a+") as file:
                file.write(f"{datetime.datetime.now()} --- INFO --- {table} DROPPED!\n")
    except Exception as error:
        raise error

def setupSiteTables(conn, site_manager: MyDataclasses.SiteManager):
    try:
        for table in site_manager.create_order:
            database.__createTable(conn, site_manager.site_name, table)
            with open("process.log", "a+") as file:
                file.write(f"{datetime.datetime.now()} --- INFO --- {table} Created!\n")
    except Exception as error:
        raise error

def addAdminUser(conn, site_manager: MyDataclasses.SiteManager, convert=True):
    admin_user = ()
    try:
        sql = f"INSERT INTO logins (username, password, email, row_type) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO UPDATE SET username = excluded.username RETURNING *;"
        with conn.cursor() as cur:
            cur.execute(sql, site_manager.admin_user)
            rows = cur.fetchone()
            if rows and convert:
                admin_user = database.tupleDictionaryFactory(cur.description, rows)
            elif rows and not convert:
                admin_user = rows   
        with open("process.log", "a+") as file:
            file.write(f"{datetime.datetime.now()} --- INFO --- Admin User Created!\n")
    except Exception as error:
        raise error
    return admin_user

def deleteSite(site_manager: MyDataclasses.SiteManager):
    """Uses a Site Manager to delete a site from the system.

    Args:
        site_manager (MyDataclasses.SiteManager): 

    Raises:
        Exception: 
    """
    database_config = config()
    print(site_manager)
    try:
        with psycopg2.connect(**database_config) as conn:
            print("before site")
            site = database.selectSiteTuple(conn, (site_manager.site_name,), convert=True)
            print("before user")
            user = database.getUser(conn, site_manager.admin_user, convert=True)
            print("after user: ", user)
            if user['id'] != site['site_owner_id']:
                raise Exception("The credentials passed do not match site owner")

            print("before roles")
            roles = database.selectRolesTuple(conn, (site['id'],), convert=True)
            database.deleteRolesTuple(conn, site['site_name'], [role['id'] for role in roles])
            
            print("dropping site")
            dropSiteTables(conn, site_manager)

            print("updating roles and sites")
            for role in roles:
                database.updateUsersRoles(conn, role['id'])
            database.updateUsersSites(conn, site['id'])
            
            site = database.deleteSitesTuple(conn, site_manager.site_name, (site['id'], ), convert=True)
            
    except Exception as error:
        with open("process.log", "a+") as file:
            file.write(f"{datetime.datetime.now()} --- ERROR --- {error}\n")
        print(error)
        conn.rollback()

def addSite(site_manager: MyDataclasses.SiteManager):
    """uses a Site Manager to add a site to the system

    Args:
        site_manager (MyDataclasses.SiteManager):
    """
    database_config = config()
    try:
        with psycopg2.connect(**database_config) as conn:
            setupSiteTables(conn, site_manager)
            
            admin_user = addAdminUser(conn, site_manager)
            
            site = MyDataclasses.SitePayload(
                site_name=site_manager.site_name,
                site_description=site_manager.description,
                site_owner_id=admin_user['id']
            )
            site = database.insertSitesTuple(conn, site.payload(), convert=True)
            
            role = MyDataclasses.RolePayload("Admin", f"Admin for {site['site_name']}", site['id'])
            role = database.insertRolesTuple(conn, role.payload(), convert=True)
            
            admin_user = database.updateAddLoginSitesRoles(conn, (site["id"], role["id"], admin_user["id"]), convert=True)
            
            default_zone = MyDataclasses.ZonePayload(site_manager.default_zone, site['id'])
            default_zone = database.insertZonesTuple(conn, site["site_name"], default_zone.payload(), convert=True)
            
            uuid = f"{site_manager.default_zone}@{site_manager.default_location}"
            default_location = MyDataclasses.LocationPayload(uuid, site_manager.default_location, default_zone['id'])
            default_location = database.insertLocationsTuple(conn, site['site_name'], default_location.payload(), convert=True)
            
            # need to update the default zones/locations for site.
            payload = {
                'id': site['id'],
                'update': {'default_zone': default_zone['id'], 
                           'default_auto_issue_location': default_location['id'],
                           'default_primary_location': default_location['id']}
            }
            database.__updateTuple(conn, site_manager.site_name, f"sites", payload)
            
            
            blank_vendor = MyDataclasses.VendorPayload("None", admin_user['id'])
            blank_brand = MyDataclasses.BrandsPayload("None")
            
            blank_vendor = database.insertVendorsTuple(conn, site['site_name'], blank_vendor.payload(), convert=True)
            blank_brand = database.insertBrandsTuple(conn, site['site_name'], blank_brand.payload(), convert=True)
            
            
            conn.commit()
    except Exception as error:
        with open("process.log", "a+") as file:
            file.write(f"{datetime.datetime.now()} --- ERROR --- {error}\n")
        conn.rollback()

def postNewBlankItem(conn, site_name: str, user_id: int, data: dict):
    site = database.selectSiteTuple(conn, (site_name,), convert=True)
    default_zone = database.__selectTuple(conn, site_name, f"{site_name}_zones", (site['default_zone'], ), convert=True)
    default_location = database.__selectTuple(conn, site_name, f"{site_name}_locations", (site['default_primary_location'],), convert=True)
    uuid = f"{default_zone['name']}@{default_location['name']}"
    
    # create logistics info
    logistics_info = MyDataclasses.LogisticsInfoPayload(
            barcode=data['barcode'], 
            primary_location=site['default_primary_location'],
            primary_zone=site['default_zone'],
            auto_issue_location=site['default_auto_issue_location'],
            auto_issue_zone=site['default_zone']
            )
    
    # create item info
    item_info = MyDataclasses.ItemInfoPayload(data['barcode'])

    # create Food Info
    food_info = MyDataclasses.FoodInfoPayload()

    logistics_info_id = 0
    item_info_id = 0
    food_info_id = 0
    brand_id = 1

    
    logistics_info = database.insertLogisticsInfoTuple(conn, site_name, logistics_info.payload(), convert=True)
    item_info = database.insertItemInfoTuple(conn, site_name, item_info.payload(), convert=True)
    food_info = database.insertFoodInfoTuple(conn, site_name, food_info.payload(), convert=True)

    name = data['name']
    name = name.replace("'", "@&apostraphe&")
    description = ""
    tags = database.lst2pgarr([])
    links = json.dumps({})
    search_string = f"&&{data['barcode']}&&{name}&&"


    item = MyDataclasses.ItemsPayload(
        data['barcode'], 
        data['name'], 
        item_info['id'], 
        logistics_info['id'], 
        food_info['id'], 
        brand=brand_id, 
        row_type="single", 
        item_type=data['subtype'], 
        search_string=search_string
        )

    item = database.insertItemTuple(conn, site_name, item.payload(), convert=True)
        
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {site_name}_locations WHERE uuid=%s;", (uuid, ))
        location_id = cur.fetchone()[0]

        
    item_location = MyDataclasses.ItemLocationPayload(item['id'], location_id)
    database.insertItemLocationsTuple(conn, site_name, item_location.payload())


    creation_tuple = MyDataclasses.TransactionPayload(
            datetime.datetime.now(),
            logistics_info['id'],
            item['barcode'],
            item['item_name'],
            "SYSTEM",
            0.0,
            "Item added to the System!",
            user_id,
            {'location': uuid}
        )

    database.insertTransactionsTuple(conn, site_name, creation_tuple.payload())


def postTransaction(conn, site_name, user_id, data: dict):
    #dict_keys(['item_id', 'logistics_info_id', 'barcode', 'item_name', 'transaction_type', 
    # 'quantity', 'description', 'cost', 'vendor', 'expires', 'location_id'])
    def quantityFactory(quantity_on_hand:float, quantity:float, transaction_type:str):
        if transaction_type == "Adjust In":
            quantity_on_hand += quantity
            return quantity_on_hand
        if transaction_type == "Adjust Out":
            quantity_on_hand -= quantity
            return quantity_on_hand
        raise Exception("The transaction type is wrong!")

    transaction_time = datetime.datetime.now()

    cost_layer = MyDataclasses.CostLayerPayload(
        aquisition_date=transaction_time,
        quantity=float(data['quantity']),
        cost=float(data['cost']),
        currency_type="USD",
        vendor=int(data['vendor']),
        expires=data['expires']
    )
    transaction = MyDataclasses.TransactionPayload(
        timestamp=transaction_time,
        logistics_info_id=int(data['logistics_info_id']),
        barcode=data['barcode'],
        name=data['item_name'],
        transaction_type=data['transaction_type'],
        quantity=float(data['quantity']),
        description=data['description'],
        user_id=user_id,
    )
    
    location = database.selectItemLocationsTuple(conn, site_name, payload=(data['item_id'], data['location_id']), convert=True)
    cost_layers: list = location['cost_layers']
    if data['transaction_type'] == "Adjust In":
        cost_layer = database.insertCostLayersTuple(conn, site_name, cost_layer.payload(), convert=True)
        cost_layers.append(cost_layer['id'])
    
    if data['transaction_type'] == "Adjust Out":
        if float(location['quantity_on_hand']) < float(data['quantity']):
            return {"error":True, "message":f"The quantity on hand in the chosen location is not enough to satisfy your transaction!"}
        cost_layers = database.selectCostLayersTuple(conn, site_name, (location['id'], ), convert=True)
        
        new_cost_layers = []
        qty = float(data['quantity'])
        for layer in cost_layers:
            if qty == 0.0:
                new_cost_layers.append(layer['id'])
            elif qty >= float(layer['quantity']):
                qty -= float(layer['quantity'])
                layer['quantity'] = 0.0
            else:
                layer['quantity'] -= qty
                new_cost_layers.append(layer['id'])
                database.__updateTuple(conn, site_name, f"{site_name}_cost_layers", {'id': layer['id'], 'update': {'quantity': layer['quantity']}})
                qty = 0.0
            
            if layer['quantity'] == 0.0:
                database.deleteCostLayersTuple(conn, site_name, (layer['id'], ))
        
        cost_layers = new_cost_layers

    quantity_on_hand = quantityFactory(float(location['quantity_on_hand']), data['quantity'], data['transaction_type'])

    updated_item_location_payload = (cost_layers, quantity_on_hand, data['item_id'], data['location_id'])
    database.updateItemLocation(conn, site_name, updated_item_location_payload)

    site_location = database.__selectTuple(conn, site_name, f"{site_name}_locations", (location['location_id'], ), convert=True)

    transaction.data = {'location': site_location['uuid']}

    database.insertTransactionsTuple(conn, site_name, transaction.payload())
    return {"error": False, "message":f"Transaction Successful!"}
 


site_manager = MyDataclasses.SiteManager(
    site_name="test",
    admin_user=("jadowyne", "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08", "jadowyne.ulve@outlook.com", 'user'),
    default_zone="DEFAULT",
    default_location="ALL",
    description="This is my test site"
)

#addSite(site_manager)
#deleteSite(site_manager)
