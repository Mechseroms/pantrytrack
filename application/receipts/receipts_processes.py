import pymupdf
import os
import PIL
import openfoodfacts
import psycopg2

from application.receipts import receipts_database
from application import database_payloads
from application.items.items_processes import postNewBlankItem
import config

def create_pdf_preview(pdf_path, output_path, size=(600, 400)):
    pdf = pymupdf.open(pdf_path)
    page = pdf[0]
    file_name = os.path.basename(pdf_path).replace('.pdf', "")
    pix = page.get_pixmap()
    img = PIL.Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    output_path = output_path + file_name + '.jpg'
    img.thumbnail(size)
    img.save(output_path)
    return file_name + '.jpg'

def linkItem(site, user_id, data, conn=None):
    """ this is a higher level function used to process a new item into the system,
    link it to another item, and update the receipt_item to the new linked item data.

    Args:
        site (_type_): _description_
        user_id (_type_): _description_
        data (_type_): {'receipt_item_id', 'linked_list_id', 'conv_factor'}
        conn (_type_, optional): Passed Connector. Defaults to None.

    Returns:
        _type_: _description_
    """
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True
    
    # Select receipt item
    receipt_item = receipts_database.selectReceiptItemsTuple(site, (data['receipt_item_id'],), conn=conn)
    # select linked item
    linked_list = receipts_database.getItemAllByID(site, (data['linked_list_id'],), conn=conn)

    if receipt_item['type'] == 'api': 
        new_item_data = {
            'barcode': receipt_item['barcode'], 
            'name': receipt_item['name'], 
            'subtype': 'FOOD'
        }
        postNewBlankItem(site, user_id, new_item_data, conn=conn)
    
    name = receipt_item['name']
    if receipt_item['name'] == "unknown":
        name = linked_list['item_name']
    if receipt_item['type'] == "new sku":
        new_item_data = {
            'barcode': receipt_item['barcode'], 
            'name': name, 
            'subtype': 'FOOD'
        }
        postNewBlankItem(site, user_id, new_item_data, conn=conn)

    new_item = receipts_database.getItemAllByBarcode(site, (receipt_item['barcode'], ), conn=conn)
    new_item = receipts_database.updateItemsTuple(site, {'id': new_item['id'], 'update':{'row_type': 'link'}}, conn=conn)


    item_link = database_payloads.ItemLinkPayload(
        new_item['barcode'],
        linked_list['id'],
        new_item,
        data['conv_factor']
    )

    receipts_database.insertItemLinksTuple(site, item_link.payload(), conn=conn)

    payload = {
        'id': receipt_item['id'], 
        'update': {
            'barcode': linked_list['barcode'],
            'name': linked_list['item_name'],
            'uom': linked_list['item_info']['uom']['id'],
            'qty': float(receipt_item['qty']*data['conv_factor']),
            'type': 'sku'
        }
    }

    receipts_database.updateReceiptItemsTuple(site, payload, conn=conn)

    if self_conn:
        conn.commit()
        conn.close()
        return False
    
    return conn

# OPEN FOOD FACTS API INTEGRATION
open_food_api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")
open_food_enabled = True

def get_open_facts(barcode):
    if open_food_enabled:
        barcode: str = barcode.replace('%', "")
        data = open_food_api.product.get(barcode)
        if data != None:
            return True, data
    return False, {}