INSERT INTO %%site_name%%_transactions
(timestamp, logistics_info_id, barcode, name, transaction_type, 
quantity, description, user_id, data) 
VALUES (%(timestamp)s, %(logistics_info_id)s, %(barcode)s, %(name)s, %(transaction_type)s, 
%(quantity)s, %(description)s, %(user_id)s, %(data)s)
RETURNING *;