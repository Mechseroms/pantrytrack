INSERT INTO %%site_name%%_item_info
(barcode, packaging, uom_quantity, uom, cost, safety_stock, lead_time_days, ai_pick, prefixes) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;