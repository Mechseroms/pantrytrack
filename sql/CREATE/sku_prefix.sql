CREATE TABLE IF NOT EXISTS %%site_name%%_sku_prefix(
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(16) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    UNIQUE (name, uuid)
);