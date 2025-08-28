CREATE TABLE IF NOT EXISTS users(
    user_uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4() NOT NULL,
    user_name VARCHAR(255) NOT NULL,
    user_password VARCHAR(255) DEFAULT NULL,
    user_email VARCHAR(255) UNIQUE NOT NULL,
    user_favorites JSONB DEFAULT '{}' NOT NULL,
    user_sites UUID [] DEFAULT '{}' NOT NULL,
    user_roles UUID [] DEFAULT '{}' NOT NULL,
    user_is_system_admin BOOLEAN DEFAULT FALSE NOT NULL,
    user_flags JSONB DEFAULT '{}' NOT NULL,
    user_row_type VARCHAR(50) DEFAULT 'user' NOT NULL,
    user_profile_pic_url VARCHAR(255) DEFAULT '' NOT NULL,
    user_login_type VARCHAR(32) DEFAULT 'Internal' NOT NULL,
    UNIQUE(user_name),
    CHECK (user_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

