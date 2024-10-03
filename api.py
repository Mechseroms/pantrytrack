from flask import Blueprint, request, render_template, redirect, session, url_for, send_file, jsonify, Response
import psycopg2
from config import config

database_api= Blueprint('database_api', __name__)

@database_api.route("/getItems")
def pagninate_items():
    print("hello")
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    offset = (page - 1) * limit

    pantry_inventory = []

    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        try:
            with conn.cursor() as cur:
                sql = f"SELECT * FROM main_items LIMIT %s OFFSET %s;"
                cur.execute(sql, (limit, offset))
                pantry_inventory = cur.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    return jsonify({'items': pantry_inventory})