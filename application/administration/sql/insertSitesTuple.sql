INSERT INTO sites
(site_name, site_description, creation_date, site_owner_id, flags, default_zone,
default_auto_issue_location, default_primary_location) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;