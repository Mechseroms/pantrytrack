CREATE TABLE IF NOT EXISTS food_info (
    id SERIAL PRIMARY KEY,
    food_groups TEXT [],
    ingrediants TEXT [],
    nutrients JSONB,
    exires BOOLEAN
);