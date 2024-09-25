CREATE TABLE brand(
    id SERIAL PRIMARY KEY, 
    brand_name VARCHAR(255),
    brand_website TEXT
    ;)

CREATE TABLE item_info(
    id SERIAL PRIMARY KEY,
    item_description TEXT,
    item_cost FLOAT,
    item_packaging VARCHAR(255),
    item_safety_stock FLOAT,
;)

CREATE TABLE item(
    id SERIAL PRIMARY KEY,
    item_name VARCHAR(255),
    brand_id INTEGER REFRENCES brand (id),
    item_info INTEGER REFRENCES item_info (id),
)