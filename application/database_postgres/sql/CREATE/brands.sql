CREATE TABLE IF NOT EXISTS %%site_name%%_brands (
    brand_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    brand_name VARCHAR(255) NOT NULL,
    UNIQUE(brand_name)
);