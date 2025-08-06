SELECT barcodes.*, row_to_json(items.*) as item
FROM %%site_name%%_barcodes barcodes
LEFT JOIN %%site_name%%_items items ON barcodes.item_uuid = items.item_uuid 
WHERE barcodes.barcode = %s;