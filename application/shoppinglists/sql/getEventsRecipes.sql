SELECT events.recipe_uuid
FROM %%site_name%%_plan_events events
WHERE events.plan_uuid IS NULL 
    AND events.event_type = 'recipe'
    AND events.recipe_uuid IS NOT NULL
    AND events.event_date_start <= %(end_date)s 
    AND events.event_date_end >= %(start_date)s;