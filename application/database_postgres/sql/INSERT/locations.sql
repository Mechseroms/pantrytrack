INSERT INTO %%site_name%%_locations
(location_shortname, location_name, zone_uuid) 
VALUES (%(location_shortname)s, %(location_name)s, %(zone_uuid)s) 
RETURNING *;