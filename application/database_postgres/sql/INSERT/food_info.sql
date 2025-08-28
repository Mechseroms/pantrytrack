INSERT INTO %%site_name%%_food_info
(
    item_uuid,
    item_food_groups,
    item_ingredients,
    item_nutrients,
    item_expires,
    item_default_expiration
) 
VALUES (
    %(item_uuid)s,
    %(item_food_groups)s,
    %(item_ingredients)s,
    %(item_nutrients)s,
    %(item_expires)s,
    %(item_default_expiration)s
) 
RETURNING *;