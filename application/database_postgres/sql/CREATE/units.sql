CREATE TABLE IF NOT EXISTS units (
    unit_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    unit_plural VARCHAR(32) NOT NULL,
    unit_single VARCHAR(32) NOT NULL,
    unit_fullname VARCHAR(255) NOT NULL,
    unit_description TEXT DEFAULT '' NOT NULL,
    unique(unit_plural),
    unique(unit_single),
    unique(unit_fullname)
);