#!/usr/bin/python 
import psycopg2 
from config import config 
import json, datetime, copy, csv, ast

def lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'

def unfoldCostLayers(cost_layers: str):
	cost_layers:list = [ast.literal_eval(item) for item in ast.literal_eval(cost_layers.replace('{', '[').replace('}', ']'))]
	return cost_layers

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

def setLogisticsDataTransaction(conn, site_name, location, logistics_info_id, qty):
	"""Sets the logistic_info for site at info_id

	Args:
		conn (Object): psycopg2.connector
		site_name (str): name of site where data is manipulated
		location (str): location to be add or append to data
		logistics_info_id (int): logistics data to be manipulated
		qty (float): qty to be added or appended

	Returns:
		str: success/error
	"""
	with open(f"sites/{site_name}/sql/unique/logistics_transactions.sql", "r+") as file:
		sql = file.read()
	try:
		with conn.cursor() as cur:
			cur.execute(f"SELECT quantity_on_hand, location_data FROM {site_name}_logistics_info WHERE id=%s;", (logistics_info_id, ))
			quantity_on_hand, location_data = cur.fetchone()
			location_data[location] = location_data.get(location, 0) + qty
			quantity_on_hand = float(quantity_on_hand + qty)
			cur.execute(sql, (quantity_on_hand, json.dumps(location_data), logistics_info_id))
	except Exception as error:
		return error
	return "success"

def handleNegativeQuantityOnHand(qty, cost_layers):
	cost_layers = [ast.literal_eval(item) for item in ast.literal_eval(cost_layers.replace('{', '[').replace('}', ']'))]
	dummy_quantity = qty
	while dummy_quantity > 0 and len(cost_layers) > 0:
		layer: list = list(cost_layers[0])
		if layer[0] < 0:
			layer[0] = layer[0] + 1
			dummy_quantity = dummy_quantity - 1
			cost_layers[0] = tuple(layer)
		if layer[0] == 0.0:
			cost_layers.pop(0)
			if dummy_quantity > 0 and len(cost_layers) > 0:
				layer = list(cost_layers[0])
	
	if dummy_quantity > 0 and len(cost_layers) == 0:
		cost_layers.append((dummy_quantity, 0.0))

	string_t = "ARRAY["
	string_y = ', '.join([f"'{layer_tuple}'::cost_layer" for layer_tuple in cost_layers])
	string_t += string_y + "]::cost_layer[]"
	return string_t

def handleNegativeQuantity(qty, cost_layers):
	cost_layers = [ast.literal_eval(item) for item in ast.literal_eval(cost_layers.replace('{', '[').replace('}', ']'))]
	dummy_quantity = qty
	while dummy_quantity < 0 and len(cost_layers) > 0:
		layer: list = list(cost_layers[0])
		layer[0] = layer[0] - 1
		dummy_quantity = dummy_quantity + 1
		cost_layers[0] = tuple(layer)
		if layer[0] == 0.0:
			cost_layers.pop(0)
			if dummy_quantity < 0 and len(cost_layers) > 0:
				layer = list(cost_layers[0])
	
	if dummy_quantity < 0 and len(cost_layers) == 0:
		cost_layers.append((dummy_quantity, 0.0))

	string_t = "ARRAY["
	string_y = ', '.join([f"'{layer_tuple}'::cost_layer" for layer_tuple in cost_layers])
	string_t += string_y + "]::cost_layer[]"
	return string_t

def setLocationData(conn, site_name, location, item_id, qty, cost):
	"""Sets location data to include barcode: qty as k:v pair

	Args:
		site_name (string): Name of the site to manipulate location data on
		location (string): location in said site to manipulate locationd data on
		barcode (string): Barcode to add or append to
		qty (float): quantity to add or append to

	Returns:
		str: error/success
	"""
	#with open(f"sites/{site_name}/sql/unique/set_location_data.sql", "r+") as file:
	#	sql = file.read()
	sql = f"UPDATE %sitename%_locations SET quantity_on_hand = %s WHERE id = %s;"
	try:
		with conn.cursor() as cur:
			cur.execute(f"SELECT id FROM {site_name}_locations WHERE uuid=%s;", (location, ))
			loc_id = cur.fetchone()
			cur.execute(f"SELECT id, quantity_on_hand, cost_layers FROM {site_name}_item_locations WHERE part_id = %s AND location_id = %s;", (item_id, loc_id))
			x = cur.fetchone()
			# maybe a while loop that will pull the cost_layers out and then go
			# through each 1 by 1 until qty is at 0...
			qty_on_hand = float(x[1]) + float(qty)
			if x[1] < 0 and qty > 0:
				# do thing
				cost_layers_string = handleNegativeQuantityOnHand(qty, x[2])
				cur.execute(f"UPDATE {site_name}_item_locations SET quantity_on_hand = %s, cost_layers = {cost_layers_string} WHERE id = %s;", (qty_on_hand, x[0]))
			elif qty < 0:
				print("ding")
				cost_layers_string = handleNegativeQuantity(qty, x[2])
				print(cost_layers_string)
				cur.execute(f"UPDATE {site_name}_item_locations SET quantity_on_hand = %s, cost_layers = {cost_layers_string} WHERE id = %s;", (qty_on_hand, x[0]))
			else:
				cur.execute(f"UPDATE {site_name}_item_locations SET quantity_on_hand = %s, cost_layers = cost_layers || ({qty}, {cost})::cost_layer WHERE id = %s;", (qty_on_hand, x[0]))
	except Exception as error:
		print(error)
		return error
	return "success"

def insertTransaction(conn, site_name, payload):
	"""Insert a transaction into the site name using a payload

	[timestamp, logistics_info_id, barcode, name, transaction_type, 
	quantity, description, user_id, data]

	Args:
		site_name (str): _description_
		payload (list): list of values to insert into database

	Returns:
		_type_: _description_
	"""
	with open(f"sites/{site_name}/sql/unique/insert_transaction.sql", "r+") as file:
		sql = file.read()
	try:
		with conn.cursor() as cur:
			cur.execute(sql, payload)
	except Exception as error:
		return error

	return "success"

def addTransaction(*, conn, site_name, payload, location, logistics_info_id, item_id, qty, cost):
	"""a complete function for adding a transaction to the system
	
	payload = [timestamp, logistics_info_id, barcode, name, transaction_type, 
	quantity, description, user_id, data]
	
	Args:
		conn (object): psycopg2.connector
		site_name (str): The site to which will have a transaction added
		payload (list): transaction payload
		location (str): location in the site that will be manipulated
		logistics_info_id (int): logistic_info id to be mainpulated
		barcode (str): barcode in the site to be manipulated
		qty (float): qty to be added or appened to the transaction

	Returns:
		str: success/error
	"""
	try:
		insertTransaction(conn, site_name, payload)
		if qty != 0.0:
			setLocationData(conn, site_name, location, item_id, qty, cost)
		#setLogisticsDataTransaction(conn, site_name, location, logistics_info_id, qty)
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		conn.rollback()
		return error

def add_food_item(site_name: str, barcode: str, name: str, payload: dict):

	# TODO: I need to validate the name so that it doesnt have characters against the SQL database schema such as ' 

	defaults = config(filename=f"sites/{site_name}/site.ini", section="defaults")
	uuid = f"{defaults["default_zone"]}@{defaults["default_primary_location"]}"
	name = name.replace("'", "@&apostraphe&")
	payload["logistics_info"]["primary_location"] = uuid
	payload["logistics_info"]["auto_issue_location"] = uuid

	tags = lst2pgarr([])
	links = json.dumps({})

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
		try:
			with conn.cursor() as cur:
				cur.execute(f"SELECT id FROM {site_name}_locations WHERE uuid=%s;", (uuid, ))
				location_id = cur.fetchone()[0]
				print(location_id)
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		sqltwo = f"INSERT INTO {site_name}_items(barcode, item_name, tags, links, item_info_id, logistics_info_id, food_info_id, row_type, item_type, search_string) VALUES('{barcode}', '{name}', '{tags}', '{links}', {item_info_id}, {logistics_info_id}, {food_info_id}, 'single', 'FOOD', '{barcode}%{name}') RETURNING *;"
		sqlthree = f"INSERT INTO {site_name}_item_locations(part_id, location_id, quantity_on_hand, cost_layers) VALUES (%s, %s, %s, %s);"
		row = None
		try:
			with conn.cursor() as cur:
				cur.execute(sqltwo)
				rows = cur.fetchone()
				if rows:
					row = rows[:]
					print(row)
				cur.execute(sqlthree, (row[0], location_id, 0.0, lst2pgarr([])))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		conn.commit()

		payload = [datetime.datetime.now(), logistics_info_id, barcode, name, "SYSTEM", 0.0, "Item added to system!", 1, json.dumps({})]
		addTransaction(conn=conn, site_name=site_name,payload=payload, location=uuid, logistics_info_id=logistics_info_id,item_id=row[0], qty=0.0, cost=0.0)

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
	drop_table(f'sites/{site_name}/sql/drop/cost_layers.sql')
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
	drop_table(f'sites/{site_name}/sql/drop/item_locations.sql')

def create_site(site_name, admin_user: tuple, default_zone, default_primary, default_auto, description):

	create_table(f'sites/{site_name}/sql/create/logins.sql')
	create_table(f"sites/{site_name}/sql/create/sites.sql")
	create_table(f"sites/{site_name}/sql/create/roles.sql")
	
	create_table(f'sites/{site_name}/sql/create/groups.sql')
	create_table(f'sites/{site_name}/sql/create/cost_layers.sql')
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
	create_table(f'sites/{site_name}/sql/create/receipts.sql')
	create_table(f'sites/{site_name}/sql/create/receipt_items.sql')
	create_table(f'sites/{site_name}/sql/create/recipes.sql')
	create_table(f'sites/{site_name}/sql/create/shopping_lists.sql')
	create_table(f'sites/{site_name}/sql/create/item_locations.sql')
	
	add_admin_sql = f"INSERT INTO logins(username, password, email) VALUES(%s, %s, %s) RETURNING id;"
	add_site_sql = f"INSERT INTO sites(site_name, creation_date, site_owner_id, flags, default_zone, default_auto_issue_location, default_primary_location, site_description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
	add_admin_role = f"INSERT INTO roles(role_name, site_id) VALUES(%s, %s) RETURNING id;"
	
	sql = f"INSERT INTO {site_name}_zones(name) VALUES (%s) RETURNING id;"
	sqltwo = f"INSERT INTO {site_name}_locations(uuid, name, zone_id, items) VALUES (%s, %s, %s, %s);"
	sqlthree = f"INSERT INTO {site_name}_vendors(vendor_name, creation_date, created_by) VALUES (%s, %s, %s);"
	
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		try:
			with conn.cursor() as cur:
				cur.execute(add_admin_sql, admin_user)
				rows = cur.fetchone()
				if rows:
					user_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		print(user_id)

		# set up site in database
		try:
			with conn.cursor() as cur:
				data = (site_name, str(datetime.datetime.now()), user_id, json.dumps({}), default_zone, default_auto, default_primary, description)
				cur.execute(add_site_sql, data)
				rows = cur.fetchone()
				if rows:
					site_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		# add admin role for site
		try:
			with conn.cursor() as cur:
				data = ('Admin', site_id)
				cur.execute(add_admin_role, data)
				rows = cur.fetchone()
				if rows:
					role_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		# update user with site_id and admin role.
		try:
			with conn.cursor() as cur:
				data = (site_id, role_id, user_id)
				cur.execute(f"UPDATE logins SET sites = sites || %s, site_roles = site_roles || %s WHERE id=%s;", data)
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		# setup the default zone.
		zone_id = None
		try:
			with conn.cursor() as cur:
				cur.execute(sql, (default_zone, ))
				rows = cur.fetchone()
				if rows:
					zone_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		uuid = f"{default_zone}@{default_primary}"

		try:
			with conn.cursor() as cur:
				cur.execute(sqltwo, (uuid, default_primary, zone_id, json.dumps({})))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		try:
			with conn.cursor() as cur:
				cur.execute(sqlthree, ("None", str(datetime.datetime.now()), 1))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		conn.commit()

async def create_site_secondary(site_name, user_id, default_zone, default_primary, default_auto, description):

	create_table(f'sites/{site_name}/sql/create/logins.sql')
	create_table(f"sites/{site_name}/sql/create/sites.sql")
	create_table(f"sites/{site_name}/sql/create/roles.sql")
	
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
	create_table(f'sites/{site_name}/sql/create/receipts.sql')
	create_table(f'sites/{site_name}/sql/create/receipt_items.sql')
	create_table(f'sites/{site_name}/sql/create/recipes.sql')
	create_table(f'sites/{site_name}/sql/create/shopping_lists.sql')
	create_table(f'sites/{site_name}/sql/create/item_locations.sql')
	
	add_site_sql = f"INSERT INTO sites(site_name, creation_date, site_owner_id, flags, default_zone, default_auto_issue_location, default_primary_location, site_description) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
	add_admin_role = f"INSERT INTO roles(role_name, site_id, role_description) VALUES(%s, %s, %s) RETURNING id;"
	
	sql = f"INSERT INTO {site_name}_zones(name) VALUES (%s) RETURNING id;"
	sqltwo = f"INSERT INTO {site_name}_locations(uuid, name, zone_id, items) VALUES (%s, %s, %s, %s);"
	sqlthree = f"INSERT INTO {site_name}_vendors(vendor_name, creation_date, created_by) VALUES (%s, %s, %s);"
	
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		# set up site in database
		try:
			with conn.cursor() as cur:
				data = (site_name, str(datetime.datetime.now()), user_id, json.dumps({}), default_zone, default_auto, default_primary, description)
				cur.execute(add_site_sql, data)
				rows = cur.fetchone()
				if rows:
					site_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		# add admin role for site
		try:
			with conn.cursor() as cur:
				data = ('Admin', site_id, f"This is the admin role for {site_name}.")
				cur.execute(add_admin_role, data)
				rows = cur.fetchone()
				if rows:
					role_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		# update user with site_id and admin role.
		try:
			with conn.cursor() as cur:
				data = (site_id, role_id, user_id)
				cur.execute(f"UPDATE logins SET sites = sites || %s, site_roles = site_roles || %s WHERE id=%s;", data)
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		# setup the default zone.
		zone_id = None
		try:
			with conn.cursor() as cur:
				cur.execute(sql, (default_zone, ))
				rows = cur.fetchone()
				if rows:
					zone_id = rows[0]
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		uuid = f"{default_zone}@{default_primary}"

		try:
			with conn.cursor() as cur:
				cur.execute(sqltwo, (uuid, default_primary, zone_id, json.dumps({})))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False
		
		try:
			with conn.cursor() as cur:
				cur.execute(sqlthree, ("None", str(datetime.datetime.now()), 1))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

		conn.commit()

	return True


def getUser(username, password):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		try:
			with conn.cursor() as cur:
				sql = f"SELECT * FROM logins WHERE username=%s;"
				cur.execute(sql, (username,))
				user = cur.fetchone()
				if user and user[2] == password:
					return list(user)
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
	return []

def setSystemAdmin(user_id: int):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		try:
			with conn.cursor() as cur:
				cur.execute(f"UPDATE logins SET system_admin = TRUE WHERE id=%s;", (user_id, ))
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False

def get_roles(site_id):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		try:
			with conn.cursor() as cur:
				cur.execute(f"SELECT * FROM roles WHERE site_id=%s;", (site_id, ))
				roles = cur.fetchall()
				return roles
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False


def get_sites(sites=[]):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		try:
			with conn.cursor() as cur:
				site_rows = []
				for each  in sites:
					cur.execute(f"SELECT * FROM sites WHERE id=%s;", (each, ))
					site_rows.append(cur.fetchone())
				print(site_rows)
				return site_rows
		except (Exception, psycopg2.DatabaseError) as error:
			print(error)
			conn.rollback()
			return False




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
		"nutrients": {
			'serving': '',
			'serving_unit': '',
			'calories': '',
			'calories_unit': 'serving',
			'proteins': '',
			'proteins_unit': '',
			'fats': '',
			'fats_unit': '',
			'carbohydrates': '',
			'carbohydrates_unit': '',
			'sugars': '',
			'sugars_unit': '',
			'sodium': '',
			'sodium_unit': '',
			'fibers': '',
			'fibers_unit': ''
		},
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
				add_food_item(site_name="main", barcode=line[1], name=line[2], payload=payload)

if __name__ == "__main__":
	parse_csv(r"C:\\Users\\jadow\\Documents\\code\\postgresql python\\postgresql-python\\2024-10-02-Pantry.csv")

