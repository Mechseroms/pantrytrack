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
    
def postNewGeneratedList(site: str, data: dict, user_id: int, conn=None):
    """data={'list_type', 'list_name', 'list_description', 'custom_items', 'uncalculated_items', 'calculated_items', 'recipes', 'full_system_calculated', 'shopping_lists'}"""
    list_type: str = data['list_type']
    list_name: str = data['list_name']
    list_description: str = data['list_description']
    custom_items: list = data['custom_items']
    uncalculated_items: list = data['uncalculated_items']
    calculated_items: list = data['calculated_items']
    recipes: list = data['recipes']
    full_system_calculated: list = data['full_system_calculated']
    shopping_lists: list = data['shopping_lists']
    site_plans: list = data['site_plans']


    self_conn=False

    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    shopping_list = database_payloads.ShoppingListPayload(
        name=list_name,
        description=list_description,
        author=int(user_id),
        sub_type="plain",
        list_type=list_type
    )
    shopping_list = shoplist_database.insertShoppingListsTuple(site, shopping_list.payload(), conn=conn)

    items_to_add_to_system = []
    # start by checcking if i should iterate full sku calc
    if full_system_calculated:
        safety_stock_items = shoplist_database.getItemsSafetyStock(site, conn=conn)
        for item in safety_stock_items:
            qty = float(item['item_info']['safety_stock']-float(item['total_sum']))
            temp_item = database_payloads.ShoppingListItemPayload(
                list_uuid=shopping_list['list_uuid'],
                item_type='calculated sku',
                item_name=item['item_name'],
                uom=item['item_info']['uom'],
                qty=qty,
                item_uuid=item['item_uuid'],
                links=item['links']
            )
            items_to_add_to_system.append(temp_item)

    if calculated_items and not full_system_calculated:
        for item_uuid in calculated_items:
            item = shoplist_database.getItemByUUID(site, {'item_uuid': item_uuid}, conn=conn)
            qty = float(item['item_info']['safety_stock']-float(item['total_sum']))
            temp_item = database_payloads.ShoppingListItemPayload(
                list_uuid=shopping_list['list_uuid'],
                item_type='calculated sku',
                item_name=item['item_name'],
                uom=item['item_info']['uom'],
                qty=qty,
                item_uuid=item['item_uuid'],
                links=item['links']
            )
            items_to_add_to_system.append(temp_item)


    if custom_items:
        for item in custom_items:
            temp_item = database_payloads.ShoppingListItemPayload(
                    list_uuid=shopping_list['list_uuid'],
                    item_type='custom',
                    item_name=item['item_name'],
                    uom=item['uom'],
                    qty=float(item['qty']),
                    item_uuid=None,
                    links={'main': item['link']}
                )
            items_to_add_to_system.append(temp_item)

    if uncalculated_items:
        for item in uncalculated_items:
            temp_item = database_payloads.ShoppingListItemPayload(
                    list_uuid=shopping_list['list_uuid'],
                    item_type='uncalculated sku',
                    item_name=item['item_name'],
                    uom=item['uom'],
                    qty=float(item['qty']),
                    item_uuid=None,
                    links={'main': item['link']}
                )
            items_to_add_to_system.append(temp_item)


    if recipes:
        for recipe_uuid in recipes:
            recipe_items = shoplist_database.getRecipeItemsByUUID(site, (recipe_uuid,), conn=conn)
            for item in recipe_items:
                temp_item = database_payloads.ShoppingListItemPayload(
                    list_uuid=shopping_list['list_uuid'],
                    item_type='recipe',
                    item_name=item['item_name'],
                    uom=item['uom'],
                    qty=float(item['qty']),
                    item_uuid=item['item_uuid'],
                    links=item['links']
                )
                items_to_add_to_system.append(temp_item)

    if shopping_lists:
        for shopping_list_uuid in shopping_lists:
            shopping_list_items = shoplist_database.getShoppingList(site, (shopping_list_uuid,), conn=conn)['sl_items']
            for item in shopping_list_items:
                temp_item = database_payloads.ShoppingListItemPayload(
                    list_uuid=shopping_list['list_uuid'],
                    item_type=item['item_type'],
                    item_name=item['item_name'],
                    uom=item['uom']['id'],
                    qty=float(item['qty']),
                    item_uuid=item['item_uuid'],
                    links=item['links']
                )
                items_to_add_to_system.append(temp_item)
    

    if site_plans:
        for site_plan in site_plans:
            if site_plan['plan_uuid'] == 'site': site_plan['plan_uuid'] = None
            plan_recipes = [event['recipe_uuid'] for event in shoplist_database.getEventRecipes(site, site_plan, conn=conn)]
            if plan_recipes:
                for recipe_uuid in plan_recipes:
                    recipe_items = shoplist_database.getRecipeItemsByUUID(site, (recipe_uuid,), conn=conn)
                    for item in recipe_items:
                        temp_item = database_payloads.ShoppingListItemPayload(
                            list_uuid=shopping_list['list_uuid'],
                            item_type='recipe',
                            item_name=item['item_name'],
                            uom=item['uom'],
                            qty=float(item['qty']),
                            item_uuid=item['item_uuid'],
                            links=item['links']
                        )
                        items_to_add_to_system.append(temp_item)

    
    if items_to_add_to_system:
        for item in items_to_add_to_system:
            shoplist_database.insertShoppingListItemsTuple(site, item.payload(), conn=conn)

    if self_conn:
        conn.commit()
        conn.close()

def deleteShoppingList(site: str, data: dict, user_id: int, conn=None):
    shopping_list_uuid = data['shopping_list_uuid']
    self_conn=False

    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    shopping_list_items = shoplist_database.getShoppingList(site, (shopping_list_uuid, ), conn=conn)['sl_items']
    shopping_list_items = [item['list_item_uuid'] for item in shopping_list_items]

    shoplist_database.deleteShoppingListsTuple(site, (shopping_list_uuid,), conn=conn)
    if shopping_list_items:
        shoplist_database.deleteShoppingListItemsTuple(site, shopping_list_items, conn=conn)


    if self_conn:
        conn.commit()
        conn.close()