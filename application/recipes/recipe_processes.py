import psycopg2
import datetime
import json

from application import database_payloads, postsqldb
from application.recipes import database_recipes
from application.items import database_items
import config

def postTransaction(site_name, user_id, data: dict, conn=None):
    """ dict_keys(['item_id', 'logistics_info_id', 'barcode', 'item_name', 'transaction_type', 
     'quantity', 'description', 'cost', 'vendor', 'expires', 'location_id'])"""
    def quantityFactory(quantity_on_hand:float, quantity:float, transaction_type:str):
        if transaction_type == "Adjust In":
            quantity_on_hand += quantity
            return quantity_on_hand
        if transaction_type == "Adjust Out":
            quantity_on_hand -= quantity
            return quantity_on_hand
        raise Exception("The transaction type is wrong!")
    
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True


    transaction_time = datetime.datetime.now()

    cost_layer = postsqldb.CostLayerPayload(
        aquisition_date=transaction_time,
        quantity=float(data['quantity']),
        cost=float(data['cost']),
        currency_type="USD",
        vendor=int(data['vendor']),
        expires=data['expires']
    )
    transaction = postsqldb.TransactionPayload(
        timestamp=transaction_time,
        logistics_info_id=int(data['logistics_info_id']),
        barcode=data['barcode'],
        name=data['item_name'],
        transaction_type=data['transaction_type'],
        quantity=float(data['quantity']),
        description=data['description'],
        user_id=user_id,
    )
    

    location = database_recipes.selectItemLocationsTuple(site_name, (data['item_id'], data['location_id']), conn=conn)
    site_location = database_recipes.selectLocationsTuple(site_name, (location['location_id'], ), conn=conn)
    cost_layers: list = location['cost_layers']
    if data['transaction_type'] == "Adjust In":
        cost_layer = database_recipes.insertCostLayersTuple(site_name, cost_layer.payload(), conn=conn)
        cost_layers.append(cost_layer['id'])
    
    if data['transaction_type'] == "Adjust Out":
        if float(location['quantity_on_hand']) < float(data['quantity']):
            raise Exception(f"The quantity on hand for {data['item_name']} in {site_location['uuid']} is not enough to satisfy your transaction!")
        cost_layers = database_recipes.selectCostLayersTuple(site_name, payload=(location['id'], ))
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
                database_recipes.updateCostLayersTuple(site_name, {'id': layer['id'], 'update': {'quantity': layer['quantity']}}, conn=conn)
                qty = 0.0
            
            if layer['quantity'] == 0.0:
                database_recipes.deleteCostLayersTuple(site_name, (layer['id'],), conn=conn)
        
        cost_layers = new_cost_layers

    quantity_on_hand = quantityFactory(float(location['quantity_on_hand']), data['quantity'], data['transaction_type'])

    updated_item_location_payload = (cost_layers, quantity_on_hand, data['item_id'], data['location_id'])
    database_recipes.updateItemLocation(site_name, updated_item_location_payload, conn=conn)
    #site_location = database_recipes.selectLocationsTuple(site_name, (location['location_id'], ), conn=conn)

    transaction.data = {'location': site_location['uuid']}

    transaction_tuple = database_recipes.insertTransactionsTuple(site_name, transaction.payload(), conn=conn)
    if self_conn:
        conn.commit()
        conn.close()
        return conn

    return conn

def process_recipe_receipt(site_name, user_id, data:dict, conn=None):
    """data={'recipe_id': recipe_id}"""

    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    recipe = database_recipes.getRecipe(site_name, (data['recipe_id'],), conn=conn)

    sku_items = [rp_item for rp_item in recipe['recipe_items'] if rp_item['item_type'] == "sku"]
    for item in sku_items:
        rp_item_uom = item['uom']['id']
        item_stuff = database_recipes.selectItemTupleByUUID(site_name, (item['item_uuid'],), conn=conn)
        conv_factor = database_recipes.selectConversionTuple(site_name, (item_stuff['item_id'], rp_item_uom))
        qty = float(item['qty']) / float(conv_factor['conv_factor'])
        payload = {
            'item_id': item_stuff['item_id'],
            'logistics_info_id': item_stuff['logistics_info_id'],
            'barcode': "",
            'item_name': item_stuff['item_name'],
            'transaction_type': "Adjust Out",
            'quantity': qty,
            'description': f"Recipe Receipt - {data['recipe_id']}",
            'cost': 0.00,
            'vendor': 0,
            'expires': False,
            'location_id': item_stuff['auto_issue_location']
            }

        try:
            postTransaction(site_name, user_id, payload, conn=conn)
        except Exception as error:
            conn.commit()
            conn.close()
            return False, str(error)

    if self_conn:
        conn.commit()
        conn.close()

    return True, ""

def postNewSkuFromRecipe(site_name: str, user_id: int, data: dict, conn=None):
    """ data = {'name', 'subtype', 'qty', 'uom_id', 'main_link', 'cost'}"""
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    site = database_recipes.selectSiteTuple((site_name,))
    default_zone = database_recipes.getZone(site_name,(site['default_zone'], ))
    default_location = database_recipes.getLocation(site_name, (site['default_primary_location'],))
    uuid = f"{default_zone['name']}@{default_location['name']}"
    
    # create logistics info
    logistics_info = database_payloads.LogisticsInfoPayload(
            barcode=None, 
            primary_location=site['default_primary_location'],
            primary_zone=site['default_zone'],
            auto_issue_location=site['default_auto_issue_location'],
            auto_issue_zone=site['default_zone']
            )
    
    # create item info
    item_info = database_payloads.ItemInfoPayload(barcode=None)

    # create Food Info
    food_info = database_payloads.FoodInfoPayload()

    logistics_info_id = 0
    item_info_id = 0
    food_info_id = 0
    brand_id = 1

    
    logistics_info = database_recipes.insertLogisticsInfoTuple(site_name, logistics_info.payload(), conn=conn)
    item_info = database_recipes.insertItemInfoTuple(site_name, item_info.payload(), conn=conn)
    food_info = database_recipes.insertFoodInfoTuple(site_name, food_info.payload(), conn=conn)

    name = data['name']
    name = name.replace("'", "@&apostraphe&")
    links = {'main': data['main_link']}
    search_string = f"&&{name}&&"


    item = database_payloads.ItemsPayload(
        barcode=None, 
        item_name=data['name'], 
        item_info_id=item_info['id'],
        item_info_uuid=item_info['item_info_uuid'], 
        logistics_info_id=logistics_info['id'], 
        logistics_info_uuid=logistics_info['logistics_info_uuid'],
        food_info_id=food_info['id'],
        food_info_uuid=food_info['food_info_uuid'],
        links=links,
        brand=brand_id, 
        row_type="single", 
        item_type=data['subtype'], 
        search_string=search_string
        )

    item = database_recipes.insertItemTuple(site_name, item.payload(), conn=conn)
        
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {site_name}_locations WHERE uuid=%s;", (uuid, ))
        location_id = cur.fetchone()[0]

    database_payloads.ItemLocationPayload
    item_location = database_payloads.ItemLocationPayload(item['id'], location_id)
    database_recipes.insertItemLocationsTuple(site_name, item_location.payload(), conn=conn)


    creation_tuple = database_payloads.TransactionPayload(
            datetime.datetime.now(),
            logistics_info['id'],
            None,
            item['item_name'],
            "SYSTEM",
            0.0,
            "Item added to the System!",
            user_id,
            {'location': uuid}
        )

    database_recipes.insertTransactionsTuple(site_name, creation_tuple.payload(), conn=conn)

    item_uuid = item['item_uuid']

    if self_conn:
        conn.commit()
        conn.close()
        return False, item_uuid
    
    return conn, item_uuid
