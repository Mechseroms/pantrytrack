CREATE TABLE IF NOT EXISTS %%site_name%%_food_info (
    item_uuid UUID PRIMARY KEY REFERENCES %%site_name%%_items(item_uuid) ON DELETE CASCADE,
    item_food_groups TEXT [] DEFAULT '{}' NOT NULL,
    item_ingredients TEXT [] DEFAULT '{}' NOT NULL,
    item_nutrients JSONB DEFAULT '{}' NOT NULL,
    item_expires BOOLEAN DEFAULT false NOT NULL,
    item_default_expiration FLOAT8 DEFAULT 0.00 NOT NULL
);