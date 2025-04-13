CREATE TABLE IF NOT EXISTS %%site_name%%_recipes (
    id SERIAL PRIMARY KEY, 
    name VARCHAR, 
    author INTEGER, 
    description TEXT, 
    creation_date TIMESTAMP,
    instructions TEXT [], 
    picture_path TEXT
);