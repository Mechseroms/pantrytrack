CREATE TABLE IF NOT EXISTS %%site_name%%_food_info (
    id SERIAL PRIMARY KEY,
    food_info_uuid UUID gen_random_uuid(),
    food_groups TEXT [],
    ingrediants TEXT [],
    nutrients JSONB,
    expires BOOLEAN,
    default_expiration FLOAT8,
    UNIQUE(food_info_uuid)
);