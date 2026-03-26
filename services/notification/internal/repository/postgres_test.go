package repository

import (
	"testing"
	"time"

	"github.com/elevenxstudios/moneylane/services/notification/internal/domain"
	"github.com/google/uuid"
)

func TestNewNotification(t *testing.T) {
	event := domain.NotificationEvent{
		EventID:   "evt-123",
		Email:     "test@example.com",
		EventType: "WAITLIST_JOINED",
	}

	n := NewNotification(event)

	if n.ID == uuid.Nil {
		t.Error("expected a generated UUID, got Nil")
	}
	if n.EventID != event.EventID {
		t.Errorf("expected EventID %s, got %s", event.EventID, n.EventID)
	}
	if n.Email != event.Email {
		t.Errorf("expected Email %s, got %s", event.Email, n.Email)
	}
	if n.EventType != event.EventType {
		t.Errorf("expected EventType %s, got %s", event.EventType, n.EventType)
	}
	if n.Status != domain.StatusPending {
		t.Errorf("expected Status %s, got %s", domain.StatusPending, n.Status)
	}
	if n.CreatedAt.IsZero() {
		t.Error("expected CreatedAt to be set")
	}
	if time.Since(n.CreatedAt) > time.Second {
		t.Errorf("expected CreatedAt to be recent, got %v", n.CreatedAt)
	}
}
