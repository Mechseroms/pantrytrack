CREATE TABLE IF NOT EXISTS roles(
    role_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4() NOT NULL,
    role_name VARCHAR(255) NOT NULL,
    role_description TEXT DEFAULT '' NOT NULL,
    role_site_uuid UUID REFERENCES sites(site_uuid) ON DELETE CASCADE NOT NULL,
    role_flags JSONB DEFAULT '{}' NOT NULL,
    UNIQUE(role_name, role_site_uuid)
);