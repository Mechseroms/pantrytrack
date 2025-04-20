import schedule, time, psycopg2
import postsqldb
from config import config

def createCycleCount():
    print("task is running")
    database_config = config()
    with psycopg2.connect(**database_config) as conn:
        sites = postsqldb.SitesTable.selectTuples(conn)
        print(sites)

        conn.rollback()

def start_schedule():
    schedule.every(1).minutes.do(createCycleCount)

    while True:
        schedule.run_pending()
        time.sleep(60)


createCycleCount()