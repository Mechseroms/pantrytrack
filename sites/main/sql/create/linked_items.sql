CREATE TABLE IF NOT EXISTS main_itemlinks (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR(255) NOt NULL,
    link INTEGER NOT NULL,
    data JSONB NOT NULL,
    conv_factor FLOAT8 NOt NULL,
    UNIQUE(barcode)
);