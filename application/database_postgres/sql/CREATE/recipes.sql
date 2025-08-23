CREATE TABLE IF NOT EXISTS %%site_name%%_recipes (
    recipe_uuid UUID PRIMARY KEY DEFAULT gen_random_uuid() NOT NULL,
    recipe_name VARCHAR(255) DEFAULT '' NOT NULL, 
    recipe_created_by INTEGER DEFAULT 1 NOT NULL, 
    recipe_description TEXT DEFAULT '' NOT NULL, 
    recipe_creation_date TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    recipe_instructions TEXT [] DEFAULT '{}' NOT NULL, 
    recipe_picture_path TEXT DEFAULT '' NOT NULL,
    UNIQUE(recipe_name)
);