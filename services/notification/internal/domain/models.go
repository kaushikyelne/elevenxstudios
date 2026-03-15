package domain

import (
	"time"

	"github.com/google/uuid"
)

// Status constants for notification lifecycle.
const (
	StatusPending = "PENDING"
	StatusSent    = "SENT"
	StatusFailed  = "FAILED"
)

// NotificationEvent represents an incoming notification request.
type NotificationEvent struct {
	EventID   string            `json:"event_id"`
	EventType string            `json:"event_type"`
	Email     string            `json:"email"`
	Metadata  map[string]string `json:"metadata,omitempty"`
}

// Notification represents a persisted notification record.
type Notification struct {
	ID        uuid.UUID
	EventID   string
	Email     string
	EventType string
	Status    string
	CreatedAt time.Time
}

// NotificationResponse is the API response body.
type NotificationResponse struct {
	Status string `json:"status"`
}
