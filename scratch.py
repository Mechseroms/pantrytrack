
from config import config 
import psycopg2, requests, database, MyDataclasses
import main, datetime, json, csv
from main import lst2pgarr
import process

def importItemFromCSV(test, site_name, uuid, site):
        logistics_info = MyDataclasses.LogisticsInfoPayload(
            barcode=test['barcode'], 
            primary_location=site['default_primary_location'],
            primary_zone=site['default_zone'],
            auto_issue_location=site['default_auto_issue_location'],
            auto_issue_zone=site['default_zone'])
        
        item_info = MyDataclasses.ItemInfoPayload(test['barcode'])


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


        food_info = MyDataclasses.FoodInfoPayload(food_groups, ingrediants, nutrients)

        if test['brands'] != "":
            brand = MyDataclasses.BrandsPayload(test['brands'])

        logistics_info_id = 0
        item_info_id = 0
        food_info_id = 0
        brand_id = 1

        database_config = config()
        try:
            with psycopg2.connect(**database_config) as conn:
                logistics_info = database.insertLogisticsInfoTuple(conn, site_name, logistics_info.payload())
                item_info = database.insertItemInfoTuple(conn, site_name, item_info.payload())
                food_info = database.insertFoodInfoTuple(conn, site_name, food_info.payload())
                if test['brands'] != "":
                    brand = database.insertBrandsTuple(conn, site_name, brand.payload())
                    brand_id = brand[0]

                print("Logistics:", logistics_info)
                print("item_info:", item_info)
                print("food_info:", food_info)
                print("brand:", brand_id)

                name = test['name']
                name = name.replace("'", "@&apostraphe&")
                description = ""
                tags = lst2pgarr([])
                links = json.dumps({})
                search_string = f"&&{test['barcode']}&&{name}&&"


                item = MyDataclasses.ItemsPayload(test['barcode'], test['name'], item_info[0], 
                                                    logistics_info[0], food_info[0], brand=brand_id, 
                                                    row_type="single", item_type=test["sub_type"], search_string=search_string)

                item = database.insertItemTuple(conn, site_name, item.payload(), convert=True)
                item = database.getItemAllByID(conn, site_name, (item['id'], ), convert=True)
                print("Item:", item)
                with conn.cursor() as cur:
                    cur.execute(f"SELECT id FROM {site_name}_locations WHERE uuid=%s;", (uuid, ))
                    location_id = cur.fetchone()[0]


                print("Location ID:", location_id)
                item_location = MyDataclasses.ItemLocationPayload(item['id'], location_id)
                location = database.insertItemLocationsTuple(conn, site_name, item_location.payload(), convert=True)

                print("Item location:", location)

                creation_tuple = MyDataclasses.TransactionPayload(
                    datetime.datetime.now(),
                    logistics_info[0],
                    item['barcode'],
                    item['item_name'],
                    "SYSTEM",
                    0.0,
                    "Item added to the System!",
                    1,
                    {'location': uuid}
                )


                database.insertTransactionsTuple(conn, site_name, creation_tuple.payload())

                qoh = float(test['qty_on_hand'])
                print(qoh, type(qoh))
                trans_type = "Adjust In"
                if qoh != 0.0:
                    if qoh >= 0.0:
                        trans_type = "Adjust In"
                    else:
                        trans_type = "Adjust Out"

                payload = {
                        'item_id': item['id'],
                        'logistics_info_id': item['logistics_info_id'],
                        'barcode': item['barcode'],
                        'item_name': item['item_name'],
                        'transaction_type': trans_type,
                        'quantity': float(qoh),
                        'description': f'creation quantity',
                        'cost': item['item_info']['cost'],
                        'vendor': 1,
                        'expires': None,
                        'location_id': location_id
                    }

                process.postTransaction(conn, site_name, 1, payload) 
                conn.commit()
        except Exception as error:
            print(error, item_info)


def importCSV(path, site_name):
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        site = database.selectSiteTuple(conn, (site_name,), convert=True)
        default_zone = database.__selectTuple(conn, site_name, f"{site_name}_zones", (site['default_zone'], ), convert=True)
        default_location = database.__selectTuple(conn, site_name, f"{site_name}_locations", (site['default_primary_location'],), convert=True)


    uuid = f"{default_zone['name']}@{default_location['name']}"
    print(uuid)
    with open(path, "r+", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            try:
                importItemFromCSV(row, site_name, uuid, site)
            except Exception as error:
                with open("process.log", "a+") as file:
                    file.write("\n")
                    file.write(f"{datetime.datetime.now()} --- CAUTION --- {error}\n")
                    file.write(f"{" "*41}{json.dumps(row)}")

#importCSV("2025-03-19-Pantry (1).csv", "main")

def importLinkFromCSV(row, site_name, conn):
    barcode = row['barcode']
    link_barcode=row['link_barcode']
    item_data=json.loads(row['data'].replace('\\j*s*o*n\\', ""))
    conv_factor=row['conv_factor']

    link_item = database.getItemAllByBarcode(conn, site_name, (link_barcode, ), convert=True)

    link = MyDataclasses.ItemLinkPayload(
        barcode=barcode,
        link=link_item['id'],
        data=item_data,
        conv_factor=conv_factor
    )

    newitem = {
            'barcode': barcode, 
            'name': item_data['name'], 
            'subtype': ''
            }

    try:
        process.postNewBlankItem(conn, site_name, 1, newitem)
    except Exception as error:
        print(error)
        pass

    lin = database.insertItemLinksTuple(conn, site_name, link.payload())
    print(lin)

def importLinksFromCSV(path, site_name):
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        with open(path, "r+", encoding="utf-8") as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    importLinkFromCSV(row, site_name, conn)
                except Exception as error:
                    with open("process.log", "a+") as file:
                        file.write("\n")
                        file.write(f"{datetime.datetime.now()} --- CAUTION --- {error}\n")
                        file.write(f"{" "*41}{json.dumps(row)}")

importLinksFromCSV("test.csv", 'test')