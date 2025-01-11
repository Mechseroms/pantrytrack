CREATE TABLE IF NOT EXISTS sites (
    id SERIAL PRIMARY KEY, 
    site_name VARCHAR(120), 
    site_description TEXT, 
    creation_date TIMESTAMP,
    site_owner_id INTEGER NOT NULL,
    flags JSONB,
    default_zone VARCHAR(32),
    default_auto_issue_location VARCHAR(32),
    default_primary_location VARCHAR(32),
    UNIQUE(site_name),
    CONSTRAINT fk_site_owner
        FOREIGN KEY(site_owner_id) 
        REFERENCES logins(id)
);