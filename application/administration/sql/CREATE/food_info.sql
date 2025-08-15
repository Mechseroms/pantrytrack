CREATE TABLE IF NOT EXISTS %%site_name%%_food_info (
    id SERIAL PRIMARY KEY,
    food_info_uuid UUID DEFAULT uuid_generate_v4(),
    food_groups TEXT [],
    ingrediants TEXT [],
    nutrients JSONB,
    expires BOOLEAN,
    default_expiration FLOAT8,
    UNIQUE(food_info_uuid)
);