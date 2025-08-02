CREATE TABLE IF NOT EXISTS %%site_name%%_cost_layers (
    id SERIAL PRIMARY KEY,
    aquisition_date TIMESTAMP NOT NULL,
    quantity FLOAT8 NOT NULL,
    cost FLOAT8 NOT NULL,
    currency_type VARCHAR(16) NOT NULL,
    expires TIMESTAMP,
    vendor INTEGER DEFAULT 0
);