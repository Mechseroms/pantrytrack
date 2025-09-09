CREATE TABLE IF NOT EXISTS %%site_name%%_plan_events(
    event_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4() NOT NULL,
    event_plan_uuid UUID REFERENCES %%site_name%%_plans(plan_uuid) ON DELETE CASCADE NOT NULL,
    event_recipe_uuid UUID DEFAULT NULL,
    event_receipt_uuid UUID DEFAULT NULL,
    event_shortname VARCHAR(64) NOT NULL,
    event_description TEXT DEFAULT '' NOT NULL,
    event_date_start TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    event_date_end TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    event_created_by INTEGER DEFAULT 1 NOT NULL,
    event_type VARCHAR(32) DEFAULT '' NOT NULL
)
