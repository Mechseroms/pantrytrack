CREATE TABLE IF NOT EXISTS %%site_name%%_items(
    item_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    item_updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    item_name VARCHAR(255) NOT NULL,
    item_description TEXT DEFAULT '' NOT NULL,
    item_tags TEXT [] DEFAULT '{}' NOT NULL,
    item_links JSONB DEFAULT '{}' NOT NULL,
    item_brand_uuid UUID DEFAULT NULL,
    item_category VARCHAR(255) NOT NULL,
    item_search_string TEXT DEFAULT '' NOT NULL,
    item_inactive BOOLEAN DEFAULT false NOT NULL,
    CONSTRAINT fk_brand
        FOREIGN KEY(item_brand_uuid)
        REFERENCES %%site_name%%_brands(brand_uuid)
        ON DELETE SET NULL
);
