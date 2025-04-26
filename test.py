from config import config
import psycopg2, ast, database, datetime, json, MyDataclasses, process, pprint
import random, uuid, csv, postsqldb

import pdf2image, os, pymupdf, PIL

from pywebpush import webpush, WebPushException


site = MyDataclasses.SitePayload(
    "testA",
    "Test site A",
    1
)

print("payload", site)
x = site.__dict__
print("dict", x)