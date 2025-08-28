INSERT INTO %%site_name%%_logistics_info
(
    item_uuid,
    item_primary_location,
    item_primary_zone,
    item_auto_issue_location,
    item_auto_issue_zone
) 
VALUES (
    %(item_uuid)s,
    %(item_primary_location)s,
    %(item_primary_zone)s,
    %(item_auto_issue_location)s,
    %(item_auto_issue_zone)s
) 
RETURNING *;