# 3RD PARTY IMPORTS
import datetime
import psycopg2
import json

# APPLICATION IMPORTS
from application.items import database_items
import application.postsqldb as db
import application.database_payloads as dbPayloads
import config

"""

items_processes.py handles more higher order workflows that a single database call would not be able to accomplish
or when more complex logics are needed.

"""

def postNewBlankItem(site_name: str, user_id: int, data: dict, conn=None):
    """ data = {'barcode', 'name', 'subtype'}"""
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    site = database_items.selectSiteTuple((site_name,))
    default_zone = database_items.getZone(site_name, (site['default_zone'], ))
    default_location = database_items.getLocation(site_name, (site['default_primary_location'],))
    uuid = f"{default_zone['name']}@{default_location['name']}"
    
    # create logistics info
    logistics_info = dbPayloads.LogisticsInfoPayload(
            barcode=data['barcode'], 
            primary_location=site['default_primary_location'],
            primary_zone=site['default_zone'],
            auto_issue_location=site['default_auto_issue_location'],
            auto_issue_zone=site['default_zone']
            )
    
    # create item info
    item_info = dbPayloads.ItemInfoPayload(data['barcode'])

    # create Food Info
    food_info = dbPayloads.FoodInfoPayload()

    logistics_info_id = 0
    item_info_id = 0
    food_info_id = 0
    brand_id = 1

    
    logistics_info = database_items.insertLogisticsInfoTuple(site_name, logistics_info.payload(), conn=conn)
    item_info = database_items.insertItemInfoTuple(site_name, item_info.payload(), conn=conn)
    food_info = database_items.insertFoodInfoTuple(site_name, food_info.payload(), conn=conn)

    name = data['name']
    name = name.replace("'", "@&apostraphe&")
    description = ""
    tags = db.lst2pgarr([])
    links = json.dumps({})
    search_string = f"&&{data['barcode']}&&{name}&&"


    item = dbPayloads.ItemsPayload(
        barcode = data['barcode'], 
        item_name = data['name'], 
        item_info_id=item_info['id'],
        item_info_uuid=item_info['item_info_uuid'],
        logistics_info_id=logistics_info['id'],
        logistics_info_uuid=logistics_info['logistics_info_uuid'],
        food_info_id=food_info['id'],
        food_info_uuid=food_info['food_info_uuid'], 
        brand=brand_id, 
        row_type="single", 
        item_type=data['subtype'], 
        search_string=search_string
        )

    item = database_items.insertItemTuple(site_name, item.payload(), conn=conn)
        
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {site_name}_locations WHERE uuid=%s;", (uuid, ))
        location_id = cur.fetchone()[0]

    dbPayloads.ItemLocationPayload
    item_location = dbPayloads.ItemLocationPayload(item['id'], location_id)
    database_items.insertItemLocationsTuple(site_name, item_location.payload(), conn=conn)


    creation_tuple = dbPayloads.TransactionPayload(
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

    database_items.postAddTransaction(site_name, creation_tuple.payload(), conn=conn)

    item_uuid = item['item_uuid']

    if self_conn:
        conn.commit()
        conn.close()
        return False, item_uuid
    
    return conn, item_uuid

def postLinkedItem(site, payload):
    """
    payload = {parent_id, child_id, user_id, conv_factor}
    """
    parent_item = database_items.getItemAllByID(site, (payload['parent_id'],))
    child_item = database_items.getItemAllByID(site, (payload['child_id'],))

    database_config = config.config()
    conn = psycopg2.connect(**database_config)
    conn.autocommit = False

    # i need to transact out ALL locations for child item.
    sum_child_qoh = 0
    for location in child_item['item_locations']:
        sum_child_qoh += location['quantity_on_hand']
        adjustment_payload = {
            'item_id': child_item['id'],
            'logistics_info_id': child_item['logistics_info_id'],
            'barcode': child_item['barcode'],
            'item_name': child_item['item_name'],
            'transaction_type': 'Adjust Out',
            'quantity': location['quantity_on_hand'],
            'description': f'Converted to {parent_item['barcode']}',
            'cost': child_item['item_info']['cost'],
            'vendor': 1,
            'expires': False,
            'location_id': location['location_id']
        }

        print(conn)
        conn = postAdjustment(site, payload['user_id'], adjustment_payload, conn=conn)
        print(conn)
        #process.postTransaction(conn, site_name, user_id, payload)

        print(sum_child_qoh)

    primary_location = database_items.selectItemLocationsTuple(site, (parent_item['id'], parent_item['logistics_info']['primary_location']['id']), convert=True)

    print(primary_location)

    adjustment_payload = {
            'item_id': parent_item['id'],
            'logistics_info_id': parent_item['logistics_info_id'],
            'barcode': parent_item['barcode'],
            'item_name': parent_item['item_name'],
            'transaction_type': 'Adjust In',
            'quantity': (float(sum_child_qoh)*float(payload['conv_factor'])),
            'description': f'Converted from {child_item['barcode']}',
            'cost': child_item['item_info']['cost'],
            'vendor': 1,
            'expires': None,
            'location_id': primary_location['location_id']
        }
    print(conn)
    conn=postAdjustment(site, payload['user_id'], adjustment_payload, conn=conn)
    print(conn)
    itemLink = db.ItemLinkPayload(
        barcode=child_item['barcode'],
        link=parent_item['id'],
        data=child_item,
        conv_factor=payload['conv_factor']
    )

    _, conn = database_items.postInsertItemLink(site, itemLink.payload(), conn=conn)
    print(conn)
    print(_['id'])
    _, conn = database_items.postUpdateItemByID(site, {'id': child_item['id'], 'update': {'row_type': 'link'}}, conn=conn)
    print(conn)
    print(_['id'])
    conn.commit()
    conn.close()

def postAdjustment(site_name, user_id, data: dict, conn=None):
    """dict_keys(['item_id', 'logistics_info_id', 'barcode', 'item_name', 'transaction_type', 
     'quantity', 'description', 'cost', 'vendor', 'expires', 'location_id'])"""
    def quantityFactory(quantity_on_hand:float, quantity:float, transaction_type:str):
        if transaction_type == "Adjust In":
            quantity_on_hand += quantity
            return quantity_on_hand
        if transaction_type == "Adjust Out":
            quantity_on_hand -= quantity
            return quantity_on_hand
        raise Exception("The transaction type is wrong!")

    transaction_time = datetime.datetime.now()
    
    self_conn = False

    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    cost_layer = db.CostLayerPayload(
        aquisition_date=transaction_time,
        quantity=float(data['quantity']),
        cost=float(data['cost']),
        currency_type="USD",
        vendor=int(data['vendor']),
        expires=data['expires']
    )
    
    transaction = db.TransactionPayload(
        timestamp=transaction_time,
        logistics_info_id=int(data['logistics_info_id']),
        barcode=data['barcode'],
        name=data['item_name'],
        transaction_type=data['transaction_type'],
        quantity=float(data['quantity']),
        description=data['description'],
        user_id=user_id,
    )
    
    location = database_items.selectItemLocationsTuple(site_name, payload=(data['item_id'], data['location_id']))
    cost_layers: list = location['cost_layers']
    if data['transaction_type'] == "Adjust In":
        cost_layer = database_items.insertCostLayersTuple(site_name, cost_layer.payload(), conn=conn)
        cost_layers.append(cost_layer['id'])
    
    if data['transaction_type'] == "Adjust Out":
        if float(location['quantity_on_hand']) < float(data['quantity']):
            pass
        else:
            cost_layers = database_items.selectCostLayersTuple(site_name, (location['id'], ))
            
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
                    database_items.postUpdateCostLayer(site_name, {'id': layer['id'], 'update': {'quantity': layer['quantity']}}, conn=conn)
                    qty = 0.0
                
                if layer['quantity'] == 0.0:
                    database_items.postDeleteCostLayer(site_name, (layer['id'], ), conn=conn)
            
            cost_layers = new_cost_layers

    quantity_on_hand = quantityFactory(float(location['quantity_on_hand']), data['quantity'], data['transaction_type'])

    updated_item_location_payload = (cost_layers, quantity_on_hand, data['item_id'], data['location_id'])
    database_items.postUpdateItemLocation(site_name, updated_item_location_payload)

    site_location = database_items.getLocation(site_name, (location['location_id'], ))

    transaction.data = {'location': site_location['uuid']}

    database_items.postAddTransaction(site_name, transaction.payload(), conn=conn)

    if self_conn:
        conn.commit()
        conn.close()
        return False
    
    return conn

def createSearchStringFromItem(item: dict):
    parameters = [f"id::{item['id']}", f"barcode::{item['barcode']}", f"name::{item['item_name']}", f"brand::{item['brand']['name']}", 
                          f"expires::{item['food_info']['expires']}", f"row_type::{item['row_type']}", f"item_type::{item['item_type']}"]
            
    for prefix in item['item_info']['prefixes']:
        parameters.append(f"prefix::{prefix['name']}")

    search_string = "&&".join(parameters)
    return search_string