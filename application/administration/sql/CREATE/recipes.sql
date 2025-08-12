CREATE TABLE IF NOT EXISTS %%site_name%%_recipes (
    id SERIAL PRIMARY KEY,
    recipe_uuid UUID DEFAULT gen_random_uuid() NOT NULL,
    name VARCHAR, 
    author INTEGER, 
    description TEXT, 
    creation_date TIMESTAMP,
    instructions TEXT [], 
    picture_path TEXT,
    UNIQUE(recipe_uuid)
);