import psycopg2
import datetime

from application.database_postgres.ItemsModel import ItemsModel
from application.database_postgres.ItemInfoModel import ItemInfoModel
from application.database_postgres.LogisticsInfoModel import LogisticsInfoModel
from application.database_postgres.FoodInfoModel import FoodInfoModel
from application.database_postgres.TransactionsModel import TransactionsModel
from application.database_postgres.ItemLocationsModel import ItemLocationsModel
from application.database_postgres.CostLayersModel import CostLayersModel
import config

def add_new_item(site: str, data: dict, user_uuid: str, conn=None):
    item_data = data.get('item_data')
    food_info = data.get('food_data', {})
    item_info = data.get('item_info', {})
    logistics_info = data.get('logistics_info', {})

    self_conn = False

    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    item_payload = ItemsModel.Payload(**item_data)

    item = ItemsModel.insert_tuple(site, item_payload.payload_dictionary(), conn=conn)

    item_info['item_uuid'] = item['item_uuid']
    item_info_payload = ItemInfoModel.Payload(**item_info)
    item_info = ItemInfoModel.insert_tuple(site, item_info_payload.payload_dictionary(), conn=conn)

    logistics_info['item_uuid'] = item['item_uuid']
    logistics_info_payload = LogisticsInfoModel.Payload(**logistics_info)
    logistics_info = LogisticsInfoModel.insert_tuple(site, logistics_info_payload.payload_dictionary(), conn=conn)


    if 'item_primary_location' in logistics_info.keys():
        items_location = ItemLocationsModel.Payload(
            item_uuid=item['item_uuid'],
            location_uuid=logistics_info['item_primary_location']
        )
        items_location = ItemLocationsModel.insert_tuple(site, items_location.payload_dictionary(), conn=conn)

    if item['item_category'] in ['FOOD', 'FOOD_PLU']:
        food_info['item_uuid'] = item['item_uuid']
        food_info_payload = FoodInfoModel.Payload(**food_info)
        food_info = FoodInfoModel.insert_tuple(site, food_info_payload.payload_dictionary(), conn=conn)


    transaction = TransactionsModel.Payload(
        item_uuid=item['item_uuid'],
        transaction_created_by=user_uuid,
        transaction_name="Item Created",
        transaction_type="SYSTEM"
    )
    transaction = TransactionsModel.insert_tuple(site, transaction.payload_dictionary(), conn=conn)

    if self_conn:
        conn.commit()
        conn.close()

def postAdjustment(site_name, user_uuid, data: dict, conn=None):
    """ This process handles manual transactions found at /items/transaction endpoint

    Args:
        site_name (_type_): _description_
        user_uuid (_type_): _description_
        data (dict): dataKEYS = {'item_uuid', 'item_name', 'transaction_type', 'transaction_quantity', 'transaction_description', 'transaction_cost', 'transaction_vendor', 'trans_action_expires', 'location_uuid'}
        conn (_type_, optional): _description_. Defaults to None.
    """
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

    transaction_data = {
        'item_uuid': data['item_uuid'],
        'transaction_created_by': user_uuid,
        'transaction_name': data['item_name'],
        'transaction_type': data['transaction_type'],
        'transaction_quantity': data['transaction_quantity'],
        'transaction_cost': data['transaction_cost'],
        'transaction_description': data['transaction_description']
    }

    transaction = TransactionsModel.Payload(**transaction_data)

    location = ItemLocationsModel.select_by_location_and_item(site_name, {'item_uuid': data['item_uuid'], 'location_uuid': data['location_uuid']})
    
    cost_layer_data = {
        'item_location_uuid': location['item_location_uuid'],
        'layer_aquisition_date': datetime.datetime.now(),
        'layer_quantity': data['transaction_quantity'],
        'layer_cost': data['transaction_cost'],
        'layer_currency_type': "USD"
        }
    
    new_cost_layer = CostLayersModel.Payload(**cost_layer_data)
    
    cost_layers = list(CostLayersModel.select_tuples_by_key(site_name, {'key': location['item_location_uuid']}, conn=conn))
    print(cost_layers)
    cost_layers.sort(key=lambda x: x['layer_aquisition_date'])
    
    if data['transaction_type'] == "Adjust In":
        CostLayersModel.insert_tuple(site_name, new_cost_layer.payload_dictionary(), conn=conn)
    
    if data['transaction_type'] == "Adjust Out":
        if float(location['item_quantity_on_hand']) < float(data['transaction_quantity']):
            pass
        else:
            qty = float(data['transaction_quantity'])
            for layer in cost_layers:
                if qty >= float(layer['layer_quantity']):
                    qty -= float(layer['layer_quantity'])
                    layer['layer_quantity'] = 0.0
                else:
                    layer['layer_quantity'] -= qty
                    CostLayersModel.update_by_layer_id(site_name, {'key': layer['layer_id'], 'update': {'layer_quantity': layer['layer_quantity']}}, conn=conn)
                    qty = 0.0
                
                if layer['layer_quantity'] == 0.0:
                    CostLayersModel.delete_by_layer_id(site_name, (layer['layer_id'],), conn=conn)
            
    quantity_on_hand = quantityFactory(float(location['item_quantity_on_hand']), data['transaction_quantity'], data['transaction_type'])

    ItemLocationsModel.update_tuple(site_name, {'key': location['item_location_uuid'], 'update': {'item_quantity_on_hand': quantity_on_hand}}, conn=conn)
    
    transaction.data = {'location': location['item_location_uuid']}

    TransactionsModel.insert_tuple(site_name, transaction.payload_dictionary(), conn=conn)

    if self_conn:
        conn.commit()
        conn.close()
        return False
    
    return conn