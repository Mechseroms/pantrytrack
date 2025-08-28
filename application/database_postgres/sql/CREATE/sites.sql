CREATE TABLE IF NOT EXISTS sites (
    site_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4() NOT NULL,
    site_name VARCHAR(120) NOT NULL, 
    site_description TEXT DEFAULT '' NOT NULL, 
    site_created_on TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    site_created_by UUID REFERENCES users(user_uuid) ON DELETE SET NULL,
    site_flags JSONB DEFAULT '{}' NOT NULL,
    site_default_zone_uuid UUID DEFAULT NULL,
    site_default_auto_issue_location_uuid UUID DEFAULT NULL,
    site_default_primary_location_uuid UUID DEFAULT NULL,
    UNIQUE(site_name)
);