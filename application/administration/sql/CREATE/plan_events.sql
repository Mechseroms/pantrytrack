CREATE TABLE IF NOT EXISTS %%site_name%%_plan_events(
    id SERIAL PRIMARY KEY,
    event_uuid UUID DEFAULT gen_random_uuid(),
    plan_uuid UUID,
    recipe_uuid UUID,
    event_shortname VARCHAR(32) NOT NULL,
    event_description TEXT,
    event_date_start TIMESTAMP NOT NULL,
    event_date_end TIMESTAMP NOT NULL,
    created_by INTEGER NOT NULL,
    event_type VARCHAR(32) NOT NULL,
    UNIQUE(event_uuid)
)
