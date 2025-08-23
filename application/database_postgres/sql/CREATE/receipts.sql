CREATE TABLE IF NOT EXISTS %%site_name%%_receipts (
    receipt_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4() NOT NULL,
    receipt_id VARCHAR (32) NOT NULL,
    receipt_status VARCHAR (64) DEFAULT 'Unresolved' NOT NULL,
    receipt_created_on TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    receipt_created_by INTEGER DEFAULT 1 NOT NULL,
    receipt_vendor_uuid UUID REFERENCES %%site_name%%_vendors(vendor_uuid) ON DELETE RESTRICT,
    receipt_files JSONB DEFAULT '{}' NOT NULL,
    UNIQUE(receipt_id)
);