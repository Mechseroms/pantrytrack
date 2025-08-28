INSERT INTO sites
(site_name, site_description, site_created_by, site_default_zone_uuid, site_default_auto_issue_location_uuid,
site_default_primary_location_uuid, site_created_on, site_flags) 
VALUES (%(site_name)s, %(site_description)s, %(site_created_by)s, %(site_default_zone_uuid)s, 
%(site_default_auto_issue_location_uuid)s, %(site_default_primary_location_uuid)s, 
%(site_created_on)s, %(site_flags)s) 
RETURNING *;