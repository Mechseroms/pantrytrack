from config import config
import psycopg2, ast, database, datetime, json, MyDataclasses

database_config = config()
with psycopg2.connect(**database_config) as conn:
    now = datetime.datetime.now()
    try:
        print(MyDataclasses.LogisticsInfoPayload.payload())
    except database.DatabaseError as error:
        print(error)
    
    #conn.rollback()