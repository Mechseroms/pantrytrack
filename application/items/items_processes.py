from application.items import database_items
import application.postsqldb as db
import config

import datetime
import psycopg2

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