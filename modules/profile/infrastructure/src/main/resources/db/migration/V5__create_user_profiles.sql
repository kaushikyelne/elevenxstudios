CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY,
    display_name VARCHAR(100),
    avatar_url VARCHAR(255),
    preferences JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Index for faster lookups (though user_id is PK, good for consistency)
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
