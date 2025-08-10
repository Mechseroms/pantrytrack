import psycopg2
import datetime

from application import database_payloads, postsqldb
from application.recipes import database_recipes
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
    print(location)
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

    database_recipes.insertTransactionsTuple(site_name, transaction.payload(), conn=conn)

    if self_conn:
        conn.commit()
        conn.close()
        return conn

    return {"error": False, "message":f"Transaction Successful!"}

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
        """ dict_keys(['item_id', 'logistics_info_id', 'barcode', 'item_name', 'transaction_type', 
        'quantity', 'description', 'cost', 'vendor', 'expires', 'location_id'])"""
        item_stuff = database_recipes.selectItemTupleByUUID(site_name, (item['item_uuid'],), conn=conn)
        print(item_stuff)
        payload = {
            'item_id': item_stuff['item_id'],
            'logistics_info_id': item_stuff['logistics_info_id'],
            'barcode': "",
            'item_name': item_stuff['item_name'],
            'transaction_type': "Adjust Out",
            'quantity': item['qty'],
            'description': f"Recipe Receipt - {data['recipe_id']}",
            'cost': 0.00,
            'vendor': 0,
            'expires': False,
            'location_id': item_stuff['auto_issue_location']
            }
        print(payload)

        try:
            postTransaction(site_name, user_id, payload, conn=conn)
        except Exception as error:
            conn.rollback()
            conn.close()
            return False, str(error)

    if self_conn:
        conn.commit()
        conn.close()

    return True, ""
