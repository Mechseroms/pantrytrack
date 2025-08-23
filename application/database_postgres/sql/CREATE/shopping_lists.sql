CREATE TABLE IF NOT EXISTS %%site_name%%_shopping_lists (
    list_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    list_type VARCHAR(32) NOT NULL,
    list_name VARCHAR(255) NOT NULL, 
    list_description TEXT DEFAULT '' NOT NULL,  
    list_created_by INTEGER DEFAULT 1 NOT NULL,
    list_created_on TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    UNIQUE(list_name)
);