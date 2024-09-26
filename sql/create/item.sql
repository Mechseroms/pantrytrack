CREATE TABLE IF NOT EXISTS items(
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(255) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    brand INTEGER,
    tags TEXT [],
    links TEXT [],
    item_info_id INTEGER NOT NULL,
    food_info_id INTEGER,
    row_type VARCHAR(255) NOT NULL,
    item_type VARCHAR(255) NOT NULL,
    search_string TEXT NOT NULL,
    quantity_on_hand FLOAT8,
    UNIQUE(barcode, item_info_id),
    CONSTRAINT fk_item_info
        FOREIGN KEY(item_info_id) 
        REFERENCES item_info(id),
    CONSTRAINT fk_food_info
        FOREIGN KEY(food_info_id)
        REFERENCES food_info(id),
    CONSTRAINT fk_brand
        FOREIGN KEY(brand)
        REFERENCES brands(id)
);
