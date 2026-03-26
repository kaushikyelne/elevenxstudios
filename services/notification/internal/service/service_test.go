package service

import (
	"context"
	"errors"
	"log/slog"
	"os"
	"strings"
	"testing"

	"github.com/elevenxstudios/moneylane/services/notification/internal/domain"
	"github.com/elevenxstudios/moneylane/services/notification/internal/repository"
)

// --- Mocks ---

type mockRepo struct {
	insertErr    error
	updateCalled bool
	updateStatus string
}

func (m *mockRepo) Insert(_ context.Context, _ *domain.Notification) error {
	return m.insertErr
}

func (m *mockRepo) UpdateStatus(_ context.Context, _ string, status string) error {
	m.updateCalled = true
	m.updateStatus = status
	return nil
}

type mockSender struct {
	sendErr   error
	callCount int
}

func (m *mockSender) Send(_ context.Context, _, _, _ string) error {
	m.callCount++
	return m.sendErr
}

// --- Tests ---

func testLogger() *slog.Logger {
	return slog.New(slog.NewTextHandler(os.Stdout, nil))
}

func TestProcess_Success(t *testing.T) {
	repo := &mockRepo{}
	sender := &mockSender{}
	svc := NewNotificationService(repo, sender, testLogger())

	status := svc.Process(context.Background(), domain.NotificationEvent{
		EventID:   "evt-1",
		EventType: "WAITLIST_JOINED",
		Email:     "test@example.com",
	})

	if status != "sent" {
		t.Errorf("expected 'sent', got '%s'", status)
	}
	if sender.callCount != 1 {
		t.Errorf("expected 1 send call, got %d", sender.callCount)
	}
	if !repo.updateCalled || repo.updateStatus != domain.StatusSent {
		t.Errorf("expected status update to SENT")
	}
}

func TestProcess_Duplicate(t *testing.T) {
	repo := &mockRepo{insertErr: repository.ErrDuplicate}
	sender := &mockSender{}
	svc := NewNotificationService(repo, sender, testLogger())

	status := svc.Process(context.Background(), domain.NotificationEvent{
		EventID:   "evt-1",
		EventType: "WAITLIST_JOINED",
		Email:     "test@example.com",
	})

	if status != "already_processed" {
		t.Errorf("expected 'already_processed', got '%s'", status)
	}
	if sender.callCount != 0 {
		t.Errorf("expected 0 send calls for duplicate, got %d", sender.callCount)
	}
}

func TestProcess_FailureAfterRetries(t *testing.T) {
	repo := &mockRepo{}
	sender := &mockSender{sendErr: errors.New("sendgrid down")}
	svc := NewNotificationService(repo, sender, testLogger())

	status := svc.Process(context.Background(), domain.NotificationEvent{
		EventID:   "evt-1",
		EventType: "WAITLIST_JOINED",
		Email:     "test@example.com",
	})

	if status != "failed" {
		t.Errorf("expected 'failed', got '%s'", status)
	}
	if sender.callCount != 3 {
		t.Errorf("expected 3 retry attempts, got %d", sender.callCount)
	}
	if !repo.updateCalled || repo.updateStatus != domain.StatusFailed {
		t.Errorf("expected status update to FAILED")
	}
}
func TestResolveEmailContent(t *testing.T) {
	tests := []struct {
		name            string
		event           domain.NotificationEvent
		expectedSubject string
		contains        string
	}{
		{
			name: "Waitlist Joined with Name",
			event: domain.NotificationEvent{
				EventType: "WAITLIST_JOINED",
				Metadata:  map[string]string{"name": "Alice"},
			},
			expectedSubject: "Welcome to MoneyLane!",
			contains:        "Hey Alice",
		},
		{
			name: "Waitlist Joined without Name",
			event: domain.NotificationEvent{
				EventType: "WAITLIST_JOINED",
			},
			expectedSubject: "Welcome to MoneyLane!",
			contains:        "Hey there",
		},
		{
			name: "Default/Unknown Event",
			event: domain.NotificationEvent{
				EventType: "UNKNOWN",
			},
			expectedSubject: "Notification from MoneyLane",
			contains:        "new notification",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			subject, body := resolveEmailContent(tt.event)
			if subject != tt.expectedSubject {
				t.Errorf("expected subject %s, got %s", tt.expectedSubject, subject)
			}
			if !contains(body, tt.contains) {
				t.Errorf("body does not contain %s: %s", tt.contains, body)
			}
		})
	}
}

func contains(s, substr string) bool {
	return strings.Contains(s, substr)
}

func TestProcess_RepoUpdateFailure(t *testing.T) {
	// The service currently ignores RepoUpdate errors, but we can verify it's attempt.
	repo := &mockRepo{}
	sender := &mockSender{}
	svc := NewNotificationService(repo, sender, testLogger())

	status := svc.Process(context.Background(), domain.NotificationEvent{
		EventID:   "evt-123",
		Email:     "test@example.com",
		EventType: "WAITLIST_JOINED",
	})

	if status != "sent" {
		t.Errorf("expected 'sent', got %s", status)
	}
	if !repo.updateCalled {
		t.Errorf("expected repo UpdateStatus to be called")
	}
}
