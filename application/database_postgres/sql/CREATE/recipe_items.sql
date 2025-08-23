CREATE TABLE IF NOT EXISTS %%site_name%%_recipe_items (
    recipe_item_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recipe_uuid UUID REFERENCES %%site_name%%_recipes(recipe_uuid) ON DELETE CASCADE NOT NULL,
    item_uuid UUID,
    recipe_item_type VARCHAR(32) DEFAULT 'custom' NOT NULL,
    recipe_item_name TEXT DEFAULT '' NOT NULL,
    recipe_item_uom INTEGER DEFAULT 1 NOT NULL,
    recipe_item_quantity FLOAT8 DEFAULT 0.00 NOT NULL,
    links JSONB DEFAULT '{"main": ""}' NOT NULL
);