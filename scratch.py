
from config import config 
import psycopg2, requests, database
import main, datetime, json, csv
from main import lst2pgarr

headers = []
test = []
with open("2024-10-02-Pantry.csv", "r+", encoding="utf-8") as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        try:
            if row['id'] == "430":
                test = row
        except:
            pass


# print(test)

# order_of_operations
# create_logistics
# create_item_info
# create_food_info
# create_brand_info
# return id of each and save, check to make sure you have id for each else drop out and do not commit
site_name = "main"
defaults = config(filename=f"sites/{site_name}/site.ini", section="defaults")
uuid = f"{defaults["default_zone"]}@{defaults["default_primary_location"]}"

logistics_info_payload = [
    test['barcode'],
    uuid,
	uuid,
	json.dumps({}), # dynamic_locations
	json.dumps({}), # location_data
	0.0 # quantity_on_hand
]

item_info_payload = [
    test['barcode'],
    lst2pgarr([]), # linked_items
    lst2pgarr([]), # shopping_lists
    lst2pgarr([]), # recipes
    lst2pgarr([]), # groups
    test['packaging'], # packaging
    test['product_quantity_unit'], # uom
    test['cost'], # cost
    test['safety_stock'], # safety_stock
    test['lead_time'], # lead_time_days
    False # ai_pick
]

# Food Info
t = ['serving', 'serving_unit', 'calories', 'calories_unit', 'proteins',
	'proteins_unit', 'fats', 'fats_unit', 'carbohydrates', 'carbohydrates_unit', 'sugars', 'sugars_unit', 'sodium', 'sodium_unit',
	'fibers', 'fibers_unit']

other_tags = [
'serving',
'serving_unit',
'calories',
'calories_unit',
'proteins_serving',
'proteins_unit',
'fat_serving',
'fat_unit',
'carbohydrates_serving',
'carbohydrates_unit',
'sugars_serving',
'sugars_unit',
'sodium_serving',
'sodium_unit',
'fiber_serving',
'fiber_unit',
]

nutriments = test['nutriments'].replace("'", '"')
nutriments = nutriments.replace("{", "").replace("}", "")
key_values = nutriments.split(", ")
nutriments = {}

if key_values != ['']:
    for s in key_values:
        s= s.split(": ")
        k = s[0].replace('"', "")
        v = s[1].replace('"', "")
        nutriments[k] = v

nutrients = {}
for i in range(len(other_tags)):
    if other_tags[i] in nutriments.keys():
        nutrients[t[i]] = nutriments[other_tags[i]]
    else:
        nutrients[t[i]] = ''

food_groups = test['food_groups_tags']
food_groups = food_groups.replace('[', "").replace("]", "")
food_groups = food_groups.replace("'", "")
food_groups = food_groups.split(", ")

ingrediants = test['ingredients_hierarchy']
ingrediants = ingrediants.replace('[', "").replace("]", "")
ingrediants = ingrediants.replace("'", "")
ingrediants = ingrediants.split(", ")

food_info_payload = [
    lst2pgarr(food_groups), # food_groups
    lst2pgarr(ingrediants), # ingrediants
    json.dumps(nutrients),
    False # expires
]

brand_payload = [test['brands'],]


logistics_info_id = 0
item_info_id = 0
food_info_id = 0
brand_id = 0

database_config = config()
with psycopg2.connect(**database_config) as conn:
    logistics_info = database.insertLogisticsInfoTuple(conn, "main", logistics_info_payload)
    item_info = database.insertItemInfoTuple(conn, "main", item_info_payload)
    food_info = database.insertFoodInfoTuple(conn, "main", food_info_payload)
    brand = database.insertBrandsTuple(conn, "main", brand_payload)

    print("Logistics:", logistics_info)
    print("item_info:", item_info)
    print("food_info:", food_info)
    print("brand:", brand)

    name = test['name']
    name = name.replace("'", "@&apostraphe&")
    description = ""
    tags = lst2pgarr([])
    links = json.dumps({})
    search_string = f"{test['barcode']}&{name}"

    item_payload = [
        test['barcode'],
        test['name'],
        brand[0],
        description,
        tags,
        links,
        item_info[0],
        logistics_info[0],
        food_info[0],
        "single",
        test["sub_type"],
        search_string
    ]

    print("Item:", item_payload)

    item = database.insertItemTuple(conn, "main", item_payload)
    print(item)
    with conn.cursor() as cur:
        cur.execute(f"SELECT id FROM {site_name}_locations WHERE uuid=%s;", (uuid, ))
        location_id = cur.fetchone()[0]


    print("Location ID:", location_id)

    item_location_payload = [
        item[0],
        location_id,
        0.0,
        main.lst2pgarr([])
    ]

    location = database.insertItemLocationsTuple(conn, site_name, item_location_payload)

    print("Item location:", location)

    creation_payload = [
        datetime.datetime.now(),
        logistics_info[0],
        test['barcode'],
        name,
        "SYSTEM",
        0.0,
        "Item Added to System!",
        1,
        json.dumps({'location': uuid})
        ]


    transaction = database.insertTransactionsTuple(conn, site_name, creation_payload)

    print("transaction:", transaction)

    qoh = float(test['qty_on_hand'])
    print(qoh, type(qoh))
    if qoh != 0.0:
        if qoh >= 0.0:
            trans_type = "Adjust In"
        else:
            trans_type = "Adjust Out"

        adjustment_payload = [
            datetime.datetime.now(),
            logistics_info[0],
            test['barcode'],
            name,
            trans_type,
            qoh,
            "",
            1,
            json.dumps({'location': uuid, 'cost': item_info[8]})
            ]

        transaction = database.insertTransactionsTuple(conn, site_name, adjustment_payload)
        print("transaction:", transaction)

        cost_layer_payload = [
            datetime.datetime.now(),
            float(qoh),
            float(test['cost']),
            'USD',
            None,
            0
        ]
        print(cost_layer_payload)
        cost_layer = database.insertCostLayersTuple(conn, site_name, cost_layer_payload)
        print("cost_layer:", cost_layer)

        layer_payload = [
            cost_layer[0],
            float(location[3]) + float(qoh),
            location_id, # location_id
            item[0]     # part_id
        ]

        print(layer_payload)
        location = database.updateItemLocation(conn, site_name, layer_payload)
        print(location)

    print("\n")
    conn.commit()

# need to insert into Item_Locations, part_id and location id



qoh = float(test['qty_on_hand'])

# transact qoh into the system