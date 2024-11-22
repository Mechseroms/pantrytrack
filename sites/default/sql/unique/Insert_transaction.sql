INSERT INTO %sitename%_transactions
(timestamp, logistics_info_id, barcode, name, transaction_type, quantity, description, user_id, data) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);