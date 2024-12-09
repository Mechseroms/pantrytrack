CREATE TABLE IF NOT EXISTS test_items(
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(255) NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    brand INTEGER,
    description TEXT,
    tags TEXT [],
    links JSONB,
    item_info_id INTEGER NOT NULL,
    logistics_info_id INTEGER NOT NULL,
    food_info_id INTEGER,
    row_type VARCHAR(255) NOT NULL,
    item_type VARCHAR(255) NOT NULL,
    search_string TEXT NOT NULL,
    UNIQUE(barcode, item_info_id),
    CONSTRAINT fk_item_info
        FOREIGN KEY(item_info_id) 
        REFERENCES test_item_info(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_food_info
        FOREIGN KEY(food_info_id)
        REFERENCES test_food_info(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_brand
        FOREIGN KEY(brand)
        REFERENCES test_brands(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_logistics_info
        FOREIGN KEY(logistics_info_id)
        REFERENCES test_logistics_info(id)
        ON DELETE CASCADE
);
