CREATE TABLE IF NOT EXISTS logins(
    id SERIAL PRIMARY KEY,
    username VARCHAR(255),
    password VARCHAR(255),
    favorites JSONB,
    unseen_pantry_items INTEGER [],
    unseen_groups INTEGER [],
    unseen_shopping_lists INTEGER [],
    unseen_recipes INTEGER [],
    seen_pantry_items INTEGER [],
    seen_groups INTEGER[],
    seen_shopping_lists INTEGER [],
    seen_recipes INTEGER [],
    flags JSONB
);

