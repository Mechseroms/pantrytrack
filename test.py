from config import config
import psycopg2, ast, database, datetime, json, MyDataclasses, process, pprint
import random, uuid, csv, postsqldb

import pdf2image, os, pymupdf, PIL

def create_pdf_preview(pdf_path, output_path, size=(128, 128)):
    pdf = pymupdf.open(pdf_path)
    page = pdf[0]
    file_name = os.path.basename(pdf_path).replace('.pdf', "")
    pix = page.get_pixmap()
    img = PIL.Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    output_path = output_path + file_name + '.jpg'
    img.thumbnail(size)
    img.save(output_path)  
    

file_path = 'static/files/receipts/Order_details_-_Walmart.com_04122025.pdf'
output_path = "static/files/receipts/previews/"

create_pdf_preview(file_path, output_path)