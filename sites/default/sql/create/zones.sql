CREATE TABLE IF NOT EXISTS %sitename%_zones(
    id SERIAL PRIMARY KEY,
    name VARCHAR(32) NOT NULL,
    UNIQUE(name)
);
