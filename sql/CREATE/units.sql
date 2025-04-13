CREATE TABLE IF NOT EXISTS units (
    id SERIAL PRIMARY KEY,
    plural VARCHAR(32),
    single VARCHAR(32),
    fullname VARCHAR(255),
    description TEXT,
    unique(plural),
    unique(single),
    unique(fullname)
);