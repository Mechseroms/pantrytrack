CREATE TABLE IF NOT EXISTS %%site_name%%_plans(
    plan_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_shortname VARCHAR(32) NOT NULL,
    plan_description TEXT,
    created_by INTEGER NOT NULL
)
