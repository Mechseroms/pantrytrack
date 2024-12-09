CREATE TABLE IF NOT EXISTS Backpack_logistics_info(
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(255) NOT NULL,
    primary_location VARCHAR(64),
    auto_issue_location VARCHAR(64),
    dynamic_locations JSONB,
    location_data JSONB,
    quantity_on_hand FLOAT8 NOT NULL,
    UNIQUE(barcode)
);