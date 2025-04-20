CREATE TABLE IF NOT EXISTS %%site_name%%_zones(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    description TEXT,
    site_id INTEGER NOT NULL,
    UNIQUE(name),
    CONSTRAINT fk_site
        FOREIGN KEY(site_id)
        REFERENCES sites(id)
);
