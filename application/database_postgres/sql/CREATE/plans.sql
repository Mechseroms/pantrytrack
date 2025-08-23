CREATE TABLE IF NOT EXISTS %%site_name%%_plans(
    plan_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_shortname VARCHAR(32) NOT NULL,
    plan_description TEXT DEFAULT '' NOT NULL,
    plan_created_by INTEGER DEFAULT 1 NOT NULL,
    plan_created_on TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
)
