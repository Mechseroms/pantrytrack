INSERT INTO %%site_name%%_transactions
(
    item_uuid,
    transaction_created_by,
    transaction_name,
    transaction_type,
    transaction_created_at,
    transaction_quantity,
    transaction_description,
    transaction_cost,
    transaction_data
) 
VALUES (
    %(item_uuid)s,
    %(transaction_created_by)s,
    %(transaction_name)s,
    %(transaction_type)s,
    %(transaction_created_at)s,
    %(transaction_quantity)s,
    %(transaction_description)s,
    %(transaction_cost)s,
    %(transaction_data)s
)
RETURNING *;