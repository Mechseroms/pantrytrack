CREATE TABLE IF NOT EXISTS %%site_name%%_shopping_lists (
    id SERIAL PRIMARY KEY,
    list_uuid UUID DEFAULT uuid_generate_v4() NOT NULL,
    list_type VARCHAR(32),
    name VARCHAR(255) NOT NULL, 
    description TEXT,  
    author INTEGER,
    creation_date TIMESTAMP, 
    sub_type VARCHAR(64),
    UNIQUE(list_uuid, name)
);