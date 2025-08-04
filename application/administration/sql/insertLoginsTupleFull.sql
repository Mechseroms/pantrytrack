INSERT INTO logins
(username, password, email, favorites, unseen_pantry_items, unseen_groups, unseen_shopping_lists,
    unseen_recipes, seen_pantry_items, seen_groups, seen_shopping_lists, seen_recipes,
    sites, site_roles, system_admin, flags, row_type) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;