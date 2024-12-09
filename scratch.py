sql = "SELECT items FROM main_locations WHERE id=1;"

from config import config 
import psycopg2, requests
import main, datetime


"""database_config = config()
with psycopg2.connect(**database_config) as conn:
    result = main.setLocationData(conn, "main", "default@all", 1, 4.0, 0.0)
    print(result)"""

url = "http://192.168.1.45:5810/resolveReceiptItem"
"""payload_receipt = {
    "receipt_id": 123456,
    "receipt_status": "Unresolved",
    "date_submitted": str(datetime.datetime.now()),
    "submitted_by": 1,
    "vendor_id": 0,
    "files": {},
    "items": [
        ("FOOD", 0, "%1234%", "test_item", 1.0, {"cost": 1.99, "EXPIRES": False}, "Unresolved"),
        ("FOOD", 0, "%1235%", "test_item", 1.0, {"cost": 1.99, "EXPIRES": False}, "Unresolved"),
        ("FOOD", 0, "%1236%", "test_item", 1.0, {"cost": 1.99, "EXPIRES": False}, "Unresolved"),
    ],
    "site_name": "main"
}"""





response = requests.post(url)

receipt_id = response.json()["receipt_id"]


print(receipt_id)
