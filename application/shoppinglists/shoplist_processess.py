import psycopg2

from application.shoppinglists import shoplist_database
from application import postsqldb, database_payloads
import config

def addRecipeItemsToList(site:str, data:dict, user_id: int, conn=None):
    """data = {'recipe_uuid', 'sl_id'}"""

    self_conn=False

    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True
    
    recipe_items = shoplist_database.getRecipeItemsByUUID(site, (data['recipe_uuid'],), conn=conn)


    # for each item build a new item payload
    for recipe_item in recipe_items:
        # add item to the table pointing to the list_uuid
        new_sl_item = database_payloads.ShoppingListItemPayload(
            list_uuid = data['list_uuid'],
            item_type='recipe',
            item_name=recipe_item['item_name'],
            uom=recipe_item['uom'],
            qty=recipe_item['qty'],
            item_uuid=recipe_item['item_uuid'],
            links=recipe_item['links']
        )
        shoplist_database.insertShoppingListItemsTuple(site, new_sl_item.payload(), conn=conn)


    if self_conn:
        conn.commit()
        conn.close()
    