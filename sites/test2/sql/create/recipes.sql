CREATE TABLE IF NOT EXISTS test2_recipes (
    id SERIAL PRIMARY KEY, 
    name VARCHAR, 
    author INTEGER, 
    description TEXT, 
    creation_date TIMESTAMP,
    custom_items JSONB, 
    pantry_items JSONB, 
    group_items JSONB,
    instructions TEXT [], 
    picture_path TEXT
);