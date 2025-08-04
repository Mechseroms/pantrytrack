SELECT %%site_name%%_receipts.*,
    logins.username as submitted_by 
FROM %%site_name%%_receipts
JOIN logins ON %%site_name%%_receipts.submitted_by = logins.id
ORDER BY %%site_name%%_receipts.id DESC
LIMIT %s 
OFFSET %s;