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

def add_item(barcode: str, name: str):
	sql = f"INSERT INTO item_info(barcode) VALUES ('{barcode}') RETURNING id;"
	database_config = config()
	item_info_id = None
	with psycopg2.connect(**database_config) as conn:
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

		sqltwo = f"INSERT INTO items(barcode, item_name, item_info_id, row_type, item_type, search_string) VALUES('{barcode}', '{name}', {item_info_id}, 'item', 'other', '{barcode}%{name}') RETURNING *;"
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
	
if __name__ == '__main__':
	drop_table('sql/drop/item_info.sql')
	drop_table('sql/drop/items.sql') 
	create_table('sql/create/logins.sql')
	create_table('sql/create/groups.sql')
	create_table('sql/create/linked_items.sql')
	create_table('sql/create/transactions.sql')
	create_table('sql/create/brands.sql')
	create_table('sql/create/food_info.sql')
	create_table('sql/create/item_info.sql')
	create_table('sql/create/item.sql')

	row = add_item(barcode='1237', name='test237')
	print(row)