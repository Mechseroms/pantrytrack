CREATE TABLE IF NOT EXISTS test2_groups(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    included_items INTEGER [],
    group_type VARCHAR(255),
    UNIQUE (name)
);