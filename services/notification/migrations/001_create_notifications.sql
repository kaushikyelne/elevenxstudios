CREATE TABLE IF NOT EXISTS notifications (
    id         UUID PRIMARY KEY,
    event_id   VARCHAR(255) UNIQUE NOT NULL,
    email      VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    status     VARCHAR(50)  NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_notifications_event_id ON notifications(event_id);
