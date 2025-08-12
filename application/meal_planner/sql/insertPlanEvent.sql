INSERT INTO %%site_name%%_plan_events
(plan_uuid, event_shortname, event_description, event_date_start, event_date_end, created_by, recipe_uuid, event_type) 
VALUES (%s, %s, %s, %s, %s, %s, %s, %s) 
RETURNING *;