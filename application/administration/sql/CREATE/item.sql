CREATE TABLE IF NOT EXISTS %%site_name%%_items(
    id SERIAL PRIMARY KEY,
    item_uuid UUID DEFAULT gen_random_uuid(),
    barcode VARCHAR(255),
    item_name VARCHAR(255) NOT NULL,
    brand INTEGER,
    description TEXT,
    tags TEXT [],
    links JSONB,
    item_info_id INTEGER NOT NULL,
    item_info_uuid UUID NOT NULL,
    logistics_info_id INTEGER NOT NULL,
    logistics_info_uuid UUID NOT NULL,
    food_info_id INTEGER,
    food_info_uuid UUID NOT NULL,
    row_type VARCHAR(255) NOT NULL,
    item_type VARCHAR(255) NOT NULL,
    search_string TEXT NOT NULL,
    UNIQUE(item_uuid),
    CONSTRAINT fk_item_info
        FOREIGN KEY(item_info_id) 
        REFERENCES %%site_name%%_item_info(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_food_info
        FOREIGN KEY(food_info_id)
        REFERENCES %%site_name%%_food_info(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_brand
        FOREIGN KEY(brand)
        REFERENCES %%site_name%%_brands(id),
    CONSTRAINT fk_logistics_info
        FOREIGN KEY(logistics_info_id)
        REFERENCES %%site_name%%_logistics_info(id)
        ON DELETE CASCADE
);
