WITH passed_id AS (SELECT %s AS passed_id),
    cte_receipt_items AS (
            SELECT items.* ,
            (SELECT COALESCE(row_to_json(un), '{}') FROM units un WHERE un.id = items.uom LIMIT 1) AS uom
            FROM %%site_name%%_receipt_items items
            WHERE items.receipt_id = (SELECT passed_id FROM passed_id)
            ORDER BY items.name ASC
        )

SELECT (SELECT passed_id FROM passed_id) AS passed_id,
     %%site_name%%_receipts.*,
     logins.username as submitted_by,
     (SELECT COALESCE(array_agg(row_to_json(ris)), '{}') FROM cte_receipt_items ris) AS receipt_items,
     row_to_json(%%site_name%%_vendors.*) as vendor
FROM %%site_name%%_receipts
JOIN logins ON %%site_name%%_receipts.submitted_by = logins.id
LEFT JOIN %%site_name%%_vendors ON %%site_name%%_receipts.vendor_id = %%site_name%%_vendors.id 
WHERE %%site_name%%_receipts.id=(SELECT passed_id FROM passed_id)