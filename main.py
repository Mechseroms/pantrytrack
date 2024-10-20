#!/usr/bin/python 
import psycopg2 
from config import config 
import json, datetime, copy, csv

def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'

def update_item_primary(site_name, barcode, new_primary: str):
	zone, location = new_primary.split("@")

	database_config = config()
	
	with psycopg2.connect(**database_config) as conn:
		zone_exists = False
		location_exists = False
		try:
			with conn.cursor() as cur:
				cur.execute(f"SELECT name FROM {site_name}_zones WHERE name=%s;", (zone, ))
				rows = cur.fetchone()
				if len(rows) > 0:
					zone_exists = True
				cur.execute(f"SELECT name FROM {site_name}_locations WHERE name=%s;", (location, ))
				rows = cur.fetchone()
				if len(rows) > 0:
					location_exists = True

			if zone_exists and location_exists:
				with conn.cursor() as cur: 
					cur.execute(f"UPDATE {site_name}_logistics_info SET primary_location = %s WHERE barcode = %s;", (new_primary, barcode))

		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

def insert_row(table_name, name):
	sql = f"INSERT INTO {table_name}(id, name) VALUES(%s, %s) RETURNING id;"
	id = None
	try:
		database_config = config()
		with psycopg2.connect(**database_config) as conn:
			with conn.cursor() as cur:
				cur.execute(sql, (1, name))
				rows = cur.fetchone()
				if rows:
					id = rows[0]
			
			conn.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		return id
		
def create_table(sql_file: str):
	conn = None
	try:
		params = config()
		conn = psycopg2.connect(**params)
		cur = conn.cursor()

		with open(sql_file, 'r') as file:
			cur.execute(file.read())
		
		cur.close()
		conn.commit() 
	except (Exception, psycopg2.DatabaseError) as error: 
		print(error) 
	finally: 
		if conn is not None: 
			conn.close()

def create_logistics_info(conn, site_name, barcode, payload):
	sql = f"INSERT INTO {site_name}_logistics_info(barcode, primary_location, auto_issue_location, dynamic_locations, location_data, quantity_on_hand) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;"
	logistics_info_id = None
	
	try:
		with conn.cursor() as cur:
			cur.execute(sql, 
			   (barcode, payload["primary_location"], payload["auto_issue_location"], json.dumps(payload["dynamic_locations"]),
	   json.dumps(payload["location_data"]), payload["quantity_on_hand"]))
			rows = cur.fetchone()
			if rows:
				logistics_info_id = rows[0]
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		conn.rollback()
		return error
	
	return logistics_info_id

def create_item_info(conn, site_name, barcode, payload):
	sql = f"INSERT INTO {site_name}_item_info(barcode, linked_items, shopping_lists, recipes, groups, packaging, uom, cost, safety_stock, lead_time_days, ai_pick) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
	item_info_id = None
	try:
		with conn.cursor() as cur:
			cur.execute(sql, (barcode, lst2pgarr(payload["linked_items"]), lst2pgarr(payload["shopping_lists"]), lst2pgarr(payload["recipes"]), 
					 lst2pgarr(payload["groups"]), payload["packaging"], payload["uom"], payload["cost"], payload["safety_stock"], payload["lead_time_days"],
					   payload["ai_pick"]))
			rows = cur.fetchone()
			if rows:
				item_info_id = rows[0]
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		conn.rollback()
		return error

	return item_info_id

def create_food_info(conn, site_name, payload):
	sql = f"INSERT INTO {site_name}_food_info(ingrediants, food_groups, nutrients, expires) VALUES (%s, %s, %s, %s) RETURNING id;"
	food_info_id = None
	try:
		with conn.cursor() as cur:
			cur.execute(sql, (lst2pgarr(payload["ingrediants"]), lst2pgarr(payload["food_groups"]), json.dumps(payload["nutrients"]), payload["expires"]))
			rows = cur.fetchone()
			if rows:
				food_info_id = rows[0]
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		conn.rollback()
		return False

	return food_info_id

def add_location(site_name, name, zone_id):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		sql = f"INSERT INTO {site_name}_locations (uuid, name, zone_id, items) VALUES (%s, %s, %s, %s);"
		zone_name = None
		try:
			with conn.cursor() as cur:
				cur.execute(f"SELECT name FROM {site_name}_zones WHERE id=%s;", (zone_id, ))
				zone_name = cur.fetchone()[0]
				print(zone_name)
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return error

		uuid = f"{zone_name}@{name}"
		try:
			with conn.cursor() as cur:
				cur.execute(sql, (uuid, name, zone_id, json.dumps({})))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return error

def add_zone(site_name, name):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		sql = f"INSERT INTO {site_name}_zones (name) VALUES (%s);"
		try:
			with conn.cursor() as cur:
				cur.execute(sql, (name,))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return error

def add_transaction(site_name, barcode, qty, user_id, transaction_type = "info", description = "", data = {}, location=None):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		with conn.cursor() as cur:
			cur.execute(f"SELECT item_name, logistics_info_id FROM {site_name}_items WHERE barcode=%s;", (barcode, ))
			item = cur.fetchone()

		with conn.cursor() as cur:
			cur.execute(f"SELECT location_data, quantity_on_hand, primary_location, barcode FROM {site_name}_logistics_info WHERE id=%s;", (item[1],))
			logistics_info = cur.fetchone()

	new_trans = copy.deepcopy(transaction_payload)
	new_trans["timestamp"] = datetime.datetime.now()
	new_trans["logistics_info_id"] = item[1]
	new_trans["barcode"] = barcode
	new_trans["user_id"] = user_id
	new_trans["name"] = item[0]
	new_trans["transaction_type"] = transaction_type
	new_trans["description"] = description
	new_trans["quantity"] = qty
	new_trans["data"] = data


	sql = f"INSERT INTO {site_name}_transactions(timestamp, logistics_info_id, barcode, name, transaction_type, quantity, description, user_id, data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		try:
			with conn.cursor() as cur:
				cur.execute(sql, (new_trans["timestamp"], new_trans["logistics_info_id"], new_trans["barcode"], new_trans["name"], new_trans["transaction_type"], 
					new_trans["quantity"], new_trans["description"], new_trans["user_id"], json.dumps(new_trans["data"])))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return error
		
		if not location:
			mover = logistics_info[2]
		else:
			mover = location

		location_items = None
		location_id = None
		try:
			with conn.cursor() as cur:
				cur.execute(f"SELECT id, items FROM {site_name}_locations WHERE uuid=%s;", (mover, ))
				location = cur.fetchone()
				if location:
					location_id = location[0]
					location_items = location[1]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return error

		if logistics_info[3] in location_items.keys():
			location_items[logistics_info[3]] = location_items[logistics_info[3]] + qty
		else:
			location_items[logistics_info[3]] = qty

		if mover in logistics_info[0].keys():
			logistics_info[0][mover] = logistics_info[0][mover] + qty 
		else:
			logistics_info[0][mover] = qty 

		qty = logistics_info[1] + qty

		set_location_data = f"UPDATE {site_name}_locations SET items = %s WHERE id = %s;"
		set_quantity_on_hand = f"UPDATE {site_name}_logistics_info SET quantity_on_hand = %s, location_data = %s WHERE id = %s;"
		try:
			with conn.cursor() as cur:
				cur.execute(set_quantity_on_hand, (qty, json.dumps(logistics_info[0]), new_trans["logistics_info_id"]))
				cur.execute(set_location_data, (json.dumps(location_items), location_id))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return error

		conn.commit()

def add_food_item(site_name: str, barcode: str, name: str, payload: dict):

	# TODO: I need to validate the name so that it doesnt have characters against the SQL database schema such as ' 

	defaults = config(filename=f"sites/{site_name}/site.ini", section="defaults")
	uuid = f"{defaults["default_zone"]}@{defaults["default_primary_location"]}"
	name = name.replace("'", "@&apostraphe&")
	payload["logistics_info"]["primary_location"] = uuid
	payload["logistics_info"]["auto_issue_location"] = uuid


	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		logistics_info_id = create_logistics_info(conn, site_name, barcode, payload["logistics_info"])
		if not logistics_info_id:
			return False
		item_info_id = create_item_info(conn, site_name, barcode, payload["item_info"])
		if not item_info_id:
			return False
		food_info_id = create_food_info(conn, site_name, payload["food_info"])
		if not food_info_id:
			return False

		sqltwo = f"INSERT INTO {site_name}_items(barcode, item_name, item_info_id, logistics_info_id, food_info_id, row_type, item_type, search_string) VALUES('{barcode}', '{name}', {item_info_id}, {logistics_info_id}, {food_info_id}, 'item', 'FOOD', '{barcode}%{name}') RETURNING *;"
		row = None
		try:
			with conn.cursor() as cur:
				cur.execute(sqltwo)
				rows = cur.fetchone()
				if rows:
					row = rows[:]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False


		conn.commit()


	add_transaction(site_name, barcode, qty=0, user_id=1, description="Added Item to System!")

def drop_table(sql_file: str):
	database_config = config()

	with open(sql_file, 'r') as sql_file:
		sql = sql_file.read()

	with psycopg2.connect(**database_config) as conn:
		try:
			with conn.cursor() as cur:
				cur.execute(sql)
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		conn.commit()
		return True

def delete_site(site_name):
	drop_table(f'sites/{site_name}/sql/drop/item_info.sql')
	drop_table(f'sites/{site_name}/sql/drop/items.sql')
	drop_table(f'sites/{site_name}/sql/drop/groups.sql')
	drop_table(f'sites/{site_name}/sql/drop/linked_items.sql')
	drop_table(f'sites/{site_name}/sql/drop/transactions.sql')
	drop_table(f'sites/{site_name}/sql/drop/brands.sql')
	drop_table(f'sites/{site_name}/sql/drop/food_info.sql')
	drop_table(f'sites/{site_name}/sql/drop/logistics_info.sql')
	drop_table(f'sites/{site_name}/sql/drop/zones.sql')
	drop_table(f'sites/{site_name}/sql/drop/locations.sql')
	drop_table(f'sites/{site_name}/sql/drop/vendors.sql')
	drop_table(f'sites/{site_name}/sql/drop/receipt_items.sql')
	drop_table(f'sites/{site_name}/sql/drop/receipts.sql')
	drop_table(f'sites/{site_name}/sql/drop/recipes.sql')
	drop_table(f'sites/{site_name}/sql/drop/shopping_lists.sql')

def create_site(site_name):

	site_config = config(f"sites/{site_name}/site.ini", 'defaults')

	create_table(f'sites/{site_name}/sql/create/logins.sql')
	create_table(f'sites/{site_name}/sql/create/groups.sql')
	create_table(f'sites/{site_name}/sql/create/linked_items.sql')
	create_table(f'sites/{site_name}/sql/create/brands.sql')
	create_table(f'sites/{site_name}/sql/create/food_info.sql')
	create_table(f'sites/{site_name}/sql/create/item_info.sql')
	create_table(f'sites/{site_name}/sql/create/logistics_info.sql')
	create_table(f'sites/{site_name}/sql/create/transactions.sql')
	create_table(f'sites/{site_name}/sql/create/item.sql')
	create_table(f'sites/{site_name}/sql/create/zones.sql')
	create_table(f'sites/{site_name}/sql/create/locations.sql')
	create_table(f'sites/{site_name}/sql/create/vendors.sql')
	create_table(f'sites/{site_name}/sql/create/receipt_items.sql')
	create_table(f'sites/{site_name}/sql/create/receipts.sql')
	create_table(f'sites/{site_name}/sql/create/recipes.sql')
	create_table(f'sites/{site_name}/sql/create/shopping_lists.sql')
	

	sql = f"INSERT INTO {site_name}_zones(name) VALUES (%s) RETURNING id;"
	sqltwo = f"INSERT INTO {site_name}_locations(uuid, name, zone_id, items) VALUES (%s, %s, %s, %s);"

	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		zone_id = None
		try:
			with conn.cursor() as cur:
				cur.execute(sql, (site_config["default_zone"], ))
				rows = cur.fetchone()
				if rows:
					zone_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		uuid = f"{site_config["default_zone"]}@{site_config["default_primary_location"]}"

		try:
			with conn.cursor() as cur:
				cur.execute(sqltwo, (uuid, site_config["default_primary_location"], zone_id, json.dumps({})))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False


		conn.commit()



transaction_payload = {
	"timestamp": None,
	"logistics_info_id": 0,
	"barcode": "",
	"name": "",
	"transaction_type": "info",
	"quantity": 0.0,
	"description": "",
	"user_id": 0,
	"data": {}
}


payload_food_item = {
	"item_info": {
		"linked_items": [],
		"shopping_lists": [],
		"recipes": [],
		"groups": [],
		"packaging": "Each",
		"uom": "Each",
		"cost": 0.0,
		"safety_stock": 0.0,
		"lead_time_days": 0.0,
		"ai_pick": False
	},
	"food_info": {
		"food_groups": [],
		"ingrediants": [],
		"nutrients": {},
		"expires": False
	},
	"logistics_info":{
		"primary_location": "",
		"auto_issue_location": "",
		"dynamic_locations": {},
		"location_data": {},
		"quantity_on_hand": 0.0
	}
}

def parse_csv(path_to_csv):

	payload = copy.deepcopy(payload_food_item)


	with open(path_to_csv, "r+", encoding="utf-8") as file:
		reader = csv.reader(file)
		for line in reader:
			if line[0] != "id":
				payload["item_info"]["packaging"] = line[10]
				payload["item_info"]["uom"] = line[13]
				if line[15] != "":
					payload["item_info"]["cost"] = line[15]
				if line[17] != "None":
					payload["item_info"]["safety_stock"] = line[17]
				qty = float(line[30])
				add_food_item(site_name="main", barcode=line[1], name=line[2], qty=qty, payload=payload)

			


if __name__ == "__main__":
	#print(add_readitem(site_name="main", barcode="1235", name="testone"))
	"""database_config = config()
	sql = "SELECT items FROM test_locations WHERE id=1;"
	with psycopg2.connect(**database_config) as conn:
		with conn.cursor() as cur:
			cur.execute(sql)

			items = cur.fetchone()[0]
			for k, v in items.items():
				print(f"{k}: {v}")
	"""
	parse_csv(r"C:\\Users\\jadow\\Documents\\code\\postgresql python\\postgresql-python\\2024-10-02-Pantry.csv")