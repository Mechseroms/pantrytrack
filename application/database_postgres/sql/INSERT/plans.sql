INSERT INTO %%site_name%%_plans
(plan_shortname, plan_description, created_by) 
VALUES (%(plan_shortname)s, %(plan_description)s, %(created_by)s) 
RETURNING *;