import psycopg2

from application.database_postgres.ItemsModel import ItemsModel
from application.database_postgres.ItemInfoModel import ItemInfoModel
from application.database_postgres.LogisticsInfoModel import LogisticsInfoModel
from application.database_postgres.FoodInfoModel import FoodInfoModel
from application.database_postgres.TransactionsModel import TransactionsModel
from application.database_postgres.ItemLocationsModel import ItemLocationsModel
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

    if item['item_category'] in ['FOOD', 'FOOD PLU']:
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