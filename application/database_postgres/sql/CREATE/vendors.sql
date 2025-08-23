CREATE TABLE IF NOT EXISTS %%site_name%%_vendors ( 
    vendor_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    vendor_name VARCHAR(255) NOT NULL,
    vendor_address VARCHAR(255) DEFAULT '' NOT NULL,
    vendor_phone_number VARCHAR(32) DEFAULT '' NOT NULL, 
    vendor_creation_date TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    vendor_created_by INTEGER NOT NULL,
    UNIQUE(vendor_name, vendor_address, vendor_phone_number) 
);