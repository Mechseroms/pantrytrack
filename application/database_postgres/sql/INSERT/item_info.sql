INSERT INTO %%site_name%%_item_info
(barcode, packaging, uom_quantity, uom, cost, safety_stock, lead_time_days, ai_pick, prefixes) 
VALUES (%(barcode)s, %(packaging)s, %(uom_quantity)s, %(uom)s, %(cost)s, %(safety_stock)s, %(lead_time_days)s, %(ai_pick)s, %(prefixes)s) 
RETURNING *;