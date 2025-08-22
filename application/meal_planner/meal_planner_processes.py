import datetime
import psycopg2

from application.meal_planner import meal_planner_database
from application import postsqldb, database_payloads
import config

def addTakeOutEvent(site, data, user_id, conn=None):
    event_date_start = datetime.datetime.strptime(data['event_date_start'], "%Y-%m-%d")
    event_date_end = datetime.datetime.strptime(data['event_date_end'], "%Y-%m-%d")

    vendor_id = data['vendor_id']

    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    receipt_id = meal_planner_database.requestNextReceiptID(site, conn=conn)

    receipt_payload = database_payloads.ReceiptPayload(
        receipt_id=f"TOR-{receipt_id}",
        receipt_status="Unresolved",
        submitted_by=user_id,
        vendor_id=vendor_id
    )

    receipt = meal_planner_database.insertReceiptsTuple(site, receipt_payload.payload(), conn=conn)

    print(receipt)

    receipt_item = database_payloads.ReceiptItemPayload(
        type = 'custom',
        receipt_id=receipt['id'],
        barcode="",
        item_uuid=None,
        name=data['event_shortname'],
        qty=data['attendees'],
        uom=1,
        data={'cost': data['cost'], 'expires': False}
    )

    receipt_item = meal_planner_database.insertReceiptItemsTuple(site, receipt_item.payload(), conn=conn)
    print(receipt_item)
    event_payload = database_payloads.PlanEventPayload(
        plan_uuid=None,
        event_shortname=data['event_shortname'],
        event_description=data['event_description'],
        event_date_start=event_date_start,
        event_date_end=event_date_end,
        created_by=user_id,
        recipe_uuid=data['recipe_uuid'],
        receipt_uuid=receipt['receipt_uuid'],
        event_type=data['event_type']
    )

    event = meal_planner_database.insertPlanEventTuple(site, event_payload.payload(), conn=conn)
    print(event)
    if self_conn:
        conn.commit()
        conn.close()
        return False
    
    return True