INSERT INTO %%site_name%%_items
(
    item_category, 
    item_name, 
    item_created_at,
    item_updated_at,
    item_description,
    item_tags,
    item_links,
    item_brand_uuid,
    item_search_string,
    item_inactive
    
    ) 
VALUES(
    %(item_category)s, 
    %(item_name)s, 
    %(item_created_at)s,
    %(item_updated_at)s,
    %(item_description)s,
    %(item_tags)s,
    %(item_links)s,
    %(item_brand_uuid)s,
    %(item_search_string)s,
    %(item_inactive)s
) 
RETURNING *;