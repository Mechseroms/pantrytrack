CREATE TABLE IF NOT EXISTS %sitename%_shopping_lists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL, 
    description TEXT, 
    pantry_items JSONB, 
    custom_items JSONB, 
    recipes JSONB, 
    groups JSONB, 
    author INTEGER,
    creation_date TIMESTAMP, 
    type VARCHAR(64),
    UNIQUE(name)
);