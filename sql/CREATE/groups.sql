CREATE TABLE IF NOT EXISTS %%site_name%%_groups(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    group_type VARCHAR(255),
    UNIQUE (name)
);