CREATE TABLE IF NOT EXISTS roles(
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(255) NOT NULL,
    role_description TEXT,
    site_id INTEGER NOT NULL,
    flags JSONB DEFAULT '{}',
    UNIQUE(role_name, site_id),
    CONSTRAINT fk_site
        FOREIGN KEY(site_id) 
        REFERENCES sites(id)
);