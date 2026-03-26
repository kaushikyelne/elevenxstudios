ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;
ALTER TABLE users ADD COLUMN external_provider VARCHAR(50);
ALTER TABLE users ADD COLUMN external_user_id VARCHAR(255);
CREATE UNIQUE INDEX idx_users_external_userid ON users(external_user_id);
