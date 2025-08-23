# 3RD PARTY IMPORTS
import pymupdf
import os
import PIL
import openfoodfacts
import psycopg2
import datetime
import pprint
# APPLICATION IMPORTS
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

def linkBarcodeToItem(site, user_id, data, conn=None):
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    receipt_item_id = data['receipt_item_id']
    payload = data['payload']
    item_uuid = payload['item_uuid']

    receipt_item = receipts_database.selectReceiptItemsTuple(site, (receipt_item_id,))
    item = receipts_database.getItemAllByUUID(site, (item_uuid,))

    barcode_tuple = database_payloads.BarcodesPayload(
        barcode=receipt_item['barcode'],
        item_uuid=item_uuid,
        in_exchange=payload['in_exchange'],
        out_exchange=payload['out_exchange'],
        descriptor=payload['descriptor']
    )

    receipts_database.insertBarcodesTuple(site, barcode_tuple.payload(), conn=conn)

    new_data = receipt_item['data']
    new_quantity = float(receipt_item['qty'] * payload['in_exchange'])
    new_data['expires'] = item['food_info']['expires']
    receipts_item_update = {'id': receipt_item_id, 'update': {
        'type': 'sku',
        'name': item['item_name'],
        'uom': item['item_info']['uom']['id'],
        'item_uuid': item['item_uuid'],
        'data': new_data,
        'qty': new_quantity
    }}

    receipts_database.updateReceiptItemsTuple(site, receipts_item_update, conn=conn)

    if self_conn:
        conn.commit()
        conn.close()
        return False
    
    return conn

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


def postService(site, user_id, data, conn=None):
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    receipt_item = receipts_database.selectReceiptItemsTuple(site, (data['line_id'],), conn=conn)

    receipts_database.updateReceiptItemsTuple(site, {'id': receipt_item['id'], 'update': {'status': "Resolved"}}, conn=conn)
    
    if self_conn:
        conn.commit()
        conn.close()
        return False
    
    return conn

def postLine(site, user_id, data, conn=None):
    self_conn = False
    if not conn:
        database_config = config.config()
        conn = psycopg2.connect(**database_config)
        conn.autocommit = False
        self_conn = True

    transaction_time = datetime.datetime.now()
    receipt_item = receipts_database.selectReceiptItemsTuple(site, (data['line_id'],), conn=conn)
    receipt = receipts_database.getReceiptByID(site, (receipt_item['receipt_id'], ), conn=conn)
    conv_factor = 1.0
    
    if receipt_item['data']['expires'] is not False:
        expiration = datetime.datetime.strptime(receipt_item['data']['expires'], "%Y-%m-%d")
    else:
        expiration = None

    #if receipt_item['type'] == 'sku':
     #   receipts_database.get
     #   linked_item = receipts_database.getLinkedItemByBarcode(site, (receipt_item['barcode'], ), conn=conn)
      #  if len(linked_item) > 1:
       #     conv_factor = linked_item['conv_factor']
        #    receipt_item['data']['linked_child'] = linked_item['barcode']

    item_uuid = receipt_item['item_uuid']
    if receipt_item['type'] == 'api':     
        new_item_data = {
            'barcode': receipt_item['barcode'], 
            'name': receipt_item['name'], 
            'subtype': 'FOOD'
        }
        _, item_uuid = postNewBlankItem(site, user_id, new_item_data, conn=conn)

    if receipt_item['type'] == "new sku":
        new_item_data = {
            'barcode': receipt_item['barcode'], 
            'name': receipt_item['name'], 
            'subtype': 'FOOD'
        }
        _, item_uuid = postNewBlankItem(site, user_id, new_item_data, conn=conn)
        barcodes_tuple = database_payloads.BarcodesPayload(
            barcode=receipt_item['barcode'],
            item_uuid=item_uuid,
            in_exchange=1.0,
            out_exchange=1.0,
            descriptor=receipt_item['name']
        )
        receipts_database.insertBarcodesTuple(site, barcodes_tuple.payload())


    item = receipts_database.getItemAllByUUID(site, (item_uuid, ), conn=conn)

    location = receipts_database.selectItemLocationsTuple(site, (item['id'], item['logistics_info']['primary_location']['id']), conn=conn)
    cost_layers: list = location['cost_layers']

    receipt_item['data']['location'] = item['logistics_info']['primary_location']['uuid']
    receipt_item['item_uuid'] = item_uuid

    transaction = database_payloads.TransactionPayload(
        timestamp=transaction_time,
        logistics_info_id=item['logistics_info_id'],
        barcode=item['barcode'],
        name=item['item_name'],
        transaction_type="Adjust In",
        quantity=(float(receipt_item['qty'])*conv_factor),
        description=f"{receipt['receipt_id']}",
        user_id=user_id,
        data=receipt_item['data']
    )

    cost_layer = database_payloads.CostLayerPayload(
        aquisition_date=transaction_time,
        quantity=float(receipt_item['qty']),
        cost=float(receipt_item['data']['cost']),
        currency_type="USD",
        vendor=receipt['vendor_id'],
        expires=expiration
    )

    cost_layer = receipts_database.insertCostLayersTuple(site, cost_layer.payload(), conn=conn)
    cost_layers.append(cost_layer['id'])

    quantity_on_hand = float(location['quantity_on_hand']) + float(receipt_item['qty'])

    updated_item_location_payload = (cost_layers, quantity_on_hand, item['id'], item['logistics_info']['primary_location']['id'])
    receipts_database.updateItemLocation(site, updated_item_location_payload, conn=conn)


    site_location = receipts_database.selectLocationsTuple(site, (location['location_id'], ), conn=conn)

    receipt_item['data']['location'] = site_location['uuid']
    receipts_database.insertTransactionsTuple(site, transaction.payload(), conn=conn)

    receipts_database.updateReceiptItemsTuple(site, {'id': receipt_item['id'], 'update': {'status': "Resolved"}}, conn=conn)
    
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