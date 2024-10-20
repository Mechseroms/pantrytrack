CREATE TABLE IF NOT EXISTS test2_vendors ( 
    id SERIAL PRIMARY KEY, 
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255), 
    creation_date TIMESTAMP NOT NULL, 
    created_by TIMESTAMP NOT NULL, 
    phone_number VARCHAR(32) 
);