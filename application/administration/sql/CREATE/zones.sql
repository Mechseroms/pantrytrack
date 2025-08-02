CREATE TABLE IF NOT EXISTS %%site_name%%_zones(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    description TEXT,
    UNIQUE(name)
);
