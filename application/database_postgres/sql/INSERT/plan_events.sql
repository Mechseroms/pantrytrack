INSERT INTO %%site_name%%_plan_events
(plan_uuid, event_shortname, event_description, event_date_start, event_date_end, 
created_by, recipe_uuid, receipt_uuid, event_type) 
VALUES (%(plan_uuid)s, %(event_shortname)s, %(event_description)s, %(event_date_start)s, %(event_date_end)s, 
%(created_by)s, %(recipe_uuid)s, %(receipt_uuid)s, %(event_type)s) 
RETURNING *;