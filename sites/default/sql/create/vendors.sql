CREATE TABLE IF NOT EXISTS %sitename%_vendors ( 
    id SERIAL PRIMARY KEY, 
    vendor_name VARCHAR(255) NOT NULL,
    vendor_address VARCHAR(255), 
    creation_date TIMESTAMP NOT NULL, 
    created_by INTEGER NOT NULL, 
    phone_number VARCHAR(32) 
);