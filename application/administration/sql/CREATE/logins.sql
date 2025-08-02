CREATE TABLE IF NOT EXISTS logins(
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    password VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    favorites JSONB DEFAULT '{}',
    unseen_pantry_items INTEGER [] DEFAULT '{}',
    unseen_groups INTEGER [] DEFAULT '{}',
    unseen_shopping_lists INTEGER [] DEFAULT '{}',
    unseen_recipes INTEGER [] DEFAULT '{}',
    seen_pantry_items INTEGER [] DEFAULT '{}',
    seen_groups INTEGER[] DEFAULT '{}',
    seen_shopping_lists INTEGER [] DEFAULT '{}',
    seen_recipes INTEGER [] DEFAULT '{}',
    sites INTEGER [] DEFAULT '{}',
    site_roles INTEGER [] DEFAULT '{}',
    system_admin BOOLEAN DEFAULT FALSE,
    flags JSONB DEFAULT '{}',
    row_type VARCHAR(50),
    UNIQUE(username),
    CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

