INSERT INTO %%site_name%%_item_info
(
    item_uuid, 
    item_uom, 
    item_packaging, 
    item_uom_quantity, 
    item_cost, 
    item_safety_stock, 
    item_lead_time_days, 
    item_ai_pick, 
    item_prefixes
    ) 
VALUES(
    %(item_uuid)s, 
    %(item_uom)s, 
    %(item_packaging)s, 
    %(item_uom_quantity)s, 
    %(item_cost)s, 
    %(item_safety_stock)s, 
    %(item_lead_time_days)s, 
    %(item_ai_pick)s, 
    %(item_prefixes)s
) 
RETURNING *;