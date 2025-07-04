# 3rd Party imports
import datetime
import psycopg2

# applications imports
from application import postsqldb, database_payloads
from application.poe import poe_database
import config

""" This module will hold all the multilayerd/complex process used in the 
point of ease module. """    


def postTransaction(site_name, user_id, data: dict, conn=None):
    '''Takes a set of data as a dictionary and inserts them into the system for passed site_name. '''
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
    
    location = poe_database.selectItemLocationsTuple(site_name, payload=(data['item_id'], data['location_id']), conn=conn)
    cost_layers: list = location['cost_layers']
    if data['transaction_type'] == "Adjust In":
        cost_layer = poe_database.insertCostLayersTuple(site_name, cost_layer.payload(), conn=conn)
        cost_layers.append(cost_layer['id'])
    
    if data['transaction_type'] == "Adjust Out":
        if float(location['quantity_on_hand']) < float(data['quantity']):
            return {"error":True, "message":f"The quantity on hand in the chosen location is not enough to satisfy your transaction!"}
        cost_layers = poe_database.selectCostLayersTuple(site_name, payload=(location['id'], ))

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
                poe_database.updateCostLayersTuple(site_name, {'id': layer['id'], 'update': {'quantity': layer['quantity']}}, conn=conn)
                qty = 0.0
            
            if layer['quantity'] == 0.0:
                poe_database.deleteCostLayersTuple(site_name, (layer['id'],), conn=conn)
        
        cost_layers = new_cost_layers

    quantity_on_hand = quantityFactory(float(location['quantity_on_hand']), data['quantity'], data['transaction_type'])

    updated_item_location_payload = (cost_layers, quantity_on_hand, data['item_id'], data['location_id'])
    poe_database.updateItemLocation(site_name, updated_item_location_payload, conn=conn)

    site_location = poe_database.selectLocationsTuple(site_name, (location['location_id'], ), conn=conn)

    transaction.data = {'location': site_location['uuid']}

    poe_database.insertTransactionsTuple(site_name, transaction.payload(), conn=conn)

    if self_conn:
        conn.commit()
        conn.close()

    return {"error": False, "message":f"Transaction Successful!"}

def post_receipt(site_name, user_id, data: dict, conn=None):
    '''Takes a list of items and opens and creates a SIR (SCANNED IN RECEIPT) into the system with the items linked
    to said receipt.'''
    # data = {'items': items}
    self_conn = False
    items = data['items']
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    receipt_id = poe_database.request_receipt_id(conn, site_name)
    receipt_id = f"SIR-{receipt_id}"
    receipt = database_payloads.ReceiptPayload(
        receipt_id=receipt_id,
        submitted_by=user_id
    )
    receipt = poe_database.insertReceiptsTuple(site_name, receipt.payload(), conn=conn)
    
    for item in items:
        receipt_item = database_payloads.ReceiptItemPayload(
            type=item['type'],
            receipt_id=receipt['id'],
            barcode=item['item']['barcode'],
            name=item['item']['item_name'],
            qty=item['item']['qty'],
            uom=item['item']['uom'],
            data=item['item']['data']
        )
        poe_database.insertReceiptItemsTuple(site_name, receipt_item.payload(), conn=conn)
    
    if self_conn:
        conn.commit()
        conn.close()

    return {"error":False, "message":"Transaction Complete!"}
