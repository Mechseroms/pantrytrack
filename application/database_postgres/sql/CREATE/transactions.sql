CREATE TABLE IF NOT EXISTS %%site_name%%_transactions (
    item_uuid UUID PRIMARY KEY REFERENCES %%site_name%%_items(item_uuid) ON DELETE CASCADE,
    transaction_uuid UUID DEFAULT uuid_generate_v4() NOT NULL;
    transaction_created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    transaction_name VARCHAR(255) DEFAULT NULL,
    transaction_type VARCHAR(64) DEFAULT '' NOT NULL,
    transaction_quantity FLOAT8 DEFAULT 0.00 NOT NULL,
    transaction_description TEXT DEFAULT '' NOT NULL,
    transaction_cost FLOAT8 DEFAULT 0.00 NOT NULL,
    transaction_created_by UUID DEFAULT NULL REFERENCES users(user_uuid) ON DELETE SET NULL,
    transaction_data JSONB DEFAULT '{}' NOT NULL
);