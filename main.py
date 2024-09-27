#!/usr/bin/python 
import psycopg2 
from config import config 


def insert_row(table_name, name):
	sql = f"INSERT INTO {table_name}(id, name) VALUES(%s, %s) RETURNING id"
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

def create_logistics_info(conn, site_name, barcode, quantity_on_hand=0.0):
	sql = f"INSERT INTO {site_name}_logistics_info(barcode, quantity_on_hand) VALUES ('{barcode}', {quantity_on_hand}) RETURNING id;"
	logistics_info_id = None
	try:
		with conn.cursor() as cur:
			cur.execute(sql)
			rows = cur.fetchone()
			if rows:
				logistics_info_id = rows[0]
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		conn.rollback()
		return False
	
	return logistics_info_id

def create_item_info(conn, site_name, barcode):
	sql = f"INSERT INTO {site_name}_item_info(barcode) VALUES ('{barcode}') RETURNING id;"
	item_info_id = None
	try:
		with conn.cursor() as cur:
			cur.execute(sql)
			rows = cur.fetchone()
			if rows:
				item_info_id = rows[0]
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		conn.rollback()
		return False

	return item_info_id

def add_item(site_name: str, barcode: str, name: str):
	database_config = config()
	with psycopg2.connect(**database_config) as conn:
		logistics_info_id = create_logistics_info(conn, site_name, barcode)
		if not logistics_info_id:
			return False
		item_info_id = create_item_info(conn, site_name, barcode)
		if not item_info_id:
			return False

		sqltwo = f"INSERT INTO {site_name}_items(barcode, item_name, item_info_id, logistics_info_id, row_type, item_type, search_string) VALUES('{barcode}', '{name}', {item_info_id}, {logistics_info_id}, 'item', 'other', '{barcode}%{name}') RETURNING *;"
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

		return row

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

def create_site(site_name):
	create_table(f'sites/{site_name}/sql/create/logins.sql')
	create_table(f'sites/{site_name}/sql/create/groups.sql')
	create_table(f'sites/{site_name}/sql/create/linked_items.sql')
	create_table(f'sites/{site_name}/sql/create/transactions.sql')
	create_table(f'sites/{site_name}/sql/create/brands.sql')
	create_table(f'sites/{site_name}/sql/create/food_info.sql')
	create_table(f'sites/{site_name}/sql/create/item_info.sql')
	create_table(f'sites/{site_name}/sql/create/logistics_info.sql')
	create_table(f'sites/{site_name}/sql/create/item.sql')


if __name__ == "__main__":
	#print(add_item(site_name="main", barcode="1235", name="testone"))
	database_config = config()
	sql = "SELECT * FROM main_logistics_info WHERE id=2;"
	with psycopg2.connect(**database_config) as conn:
		with conn.cursor() as cur:
			cur.execute(sql)

			rows = cur.fetchone()
			print(rows)
			print(type(rows[5]))