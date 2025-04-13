CREATE TABLE IF NOT EXISTS %%site_name%%_food_info (
    id SERIAL PRIMARY KEY,
    food_groups TEXT [],
    ingrediants TEXT [],
    nutrients JSONB,
    expires BOOLEAN,
    default_expiration FLOAT8
);