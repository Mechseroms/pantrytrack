CREATE TABLE IF NOT EXISTS test_food_info (
    id SERIAL PRIMARY KEY,
    food_groups TEXT [],
    ingrediants TEXT [],
    nutrients JSONB,
    expires BOOLEAN
);