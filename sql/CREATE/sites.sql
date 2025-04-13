CREATE TABLE IF NOT EXISTS sites (
    id SERIAL PRIMARY KEY, 
    site_name VARCHAR(120), 
    site_description TEXT, 
    creation_date TIMESTAMP,
    site_owner_id INTEGER NOT NULL,
    flags JSONB,
    default_zone INTEGER DEFAULT NULL,
    default_auto_issue_location INTEGER DEFAULT NULL,
    default_primary_location INTEGER DEFAULT NULL,
    UNIQUE(site_name)
);