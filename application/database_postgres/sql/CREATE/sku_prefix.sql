CREATE TABLE IF NOT EXISTS %%site_name%%_sku_prefix(
    sku_prefix_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sku_prefix_identifier VARCHAR (32) NOT NULL,
    sku_prefix_name VARCHAR(255) DEFAULT '' NOT NULL,
    sku_prefix_description TEXT DEFAULT '' NOT NULL,
    UNIQUE (sku_prefix_identifier, sku_prefix_name)
);