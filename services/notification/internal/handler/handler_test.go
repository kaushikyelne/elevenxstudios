package handler

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"log/slog"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/elevenxstudios/moneylane/services/notification/internal/domain"
	"github.com/elevenxstudios/moneylane/services/notification/internal/repository"
	"github.com/elevenxstudios/moneylane/services/notification/internal/service"
)

// --- Mocks ---

type mockRepo struct {
	insertErr error
}

func (m *mockRepo) Insert(_ context.Context, _ *domain.Notification) error {
	return m.insertErr
}

func (m *mockRepo) UpdateStatus(_ context.Context, _ string, _ string) error {
	return nil
}

type mockSender struct {
	sendErr error
}

func (m *mockSender) Send(_ context.Context, _, _, _ string) error {
	return m.sendErr
}

// --- Tests ---

func TestHealthCheck(t *testing.T) {
	h := NewHandler(nil, slog.New(slog.NewTextHandler(io.Discard, nil)))
	req := httptest.NewRequest("GET", "/notifications/health", nil)
	w := httptest.NewRecorder()

	h.HealthCheck(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("expected 200, got %d", w.Code)
	}

	var res map[string]string
	json.NewDecoder(w.Body).Decode(&res)
	if res["status"] != "ok" {
		t.Errorf("expected status ok, got %v", res["status"])
	}
}

func TestSendNotification(t *testing.T) {
	logger := slog.New(slog.NewTextHandler(io.Discard, nil))

	tests := []struct {
		name           string
		event          domain.NotificationEvent
		mockInsertErr  error
		mockSendErr    error
		expectedStatus int
		expectedBody   string
	}{
		{
			name: "Success",
			event: domain.NotificationEvent{
				EventID:   "evt-123",
				Email:     "user@example.com",
				EventType: "WAITLIST_JOINED",
			},
			expectedStatus: http.StatusOK,
			expectedBody:   "sent",
		},
		{
			name: "Duplicate",
			event: domain.NotificationEvent{
				EventID:   "evt-123",
				Email:     "user@example.com",
				EventType: "WAITLIST_JOINED",
			},
			mockInsertErr:  repository.ErrDuplicate,
			expectedStatus: http.StatusOK,
			expectedBody:   "already_processed",
		},
		{
			name: "Invalid Request - Missing EventID",
			event: domain.NotificationEvent{
				Email:     "user@example.com",
				EventType: "WAITLIST_JOINED",
			},
			expectedStatus: http.StatusBadRequest,
			expectedBody:   "missing_event_id",
		},
		{
			name: "Internal Error - Service Failed",
			event: domain.NotificationEvent{
				EventID:   "evt-123",
				Email:     "user@example.com",
				EventType: "WAITLIST_JOINED",
			},
			mockSendErr:    errors.New("provider error"), // service.Process returns "failed" if send fails after max retries
			expectedStatus: http.StatusInternalServerError,
			expectedBody:   "failed",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			repo := &mockRepo{insertErr: tt.mockInsertErr}
			sender := &mockSender{sendErr: tt.mockSendErr}
			svc := service.NewNotificationService(repo, sender, logger)
			h := NewHandler(svc, logger)

			body, _ := json.Marshal(tt.event)
			req := httptest.NewRequest("POST", "/notifications/email", bytes.NewReader(body))
			w := httptest.NewRecorder()

			h.SendNotification(w, req)

			if w.Code != tt.expectedStatus {
				t.Errorf("expected %d, got %d", tt.expectedStatus, w.Code)
			}

			var res domain.NotificationResponse
			json.NewDecoder(w.Body).Decode(&res)
			if res.Status != tt.expectedBody {
				t.Errorf("expected status %s, got %s", tt.expectedBody, res.Status)
			}
		})
	}
}

func TestValidateEvent(t *testing.T) {
	tests := []struct {
		name    string
		event   domain.NotificationEvent
		wantErr string
	}{
		{"Valid", domain.NotificationEvent{EventID: "1", Email: "a@b.com", EventType: "T"}, ""},
		{"MissingID", domain.NotificationEvent{Email: "a@b.com", EventType: "T"}, "missing_event_id"},
		{"MissingEmail", domain.NotificationEvent{EventID: "1", EventType: "T"}, "missing_email"},
		{"MissingType", domain.NotificationEvent{EventID: "1", Email: "a@b.com"}, "missing_event_type"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := validateEvent(tt.event)
			if tt.wantErr == "" {
				if err != nil {
					t.Errorf("expected no error, got %v", err)
				}
			} else {
				if err == nil || err.Error() != tt.wantErr {
					t.Errorf("expected error %s, got %v", tt.wantErr, err)
				}
			}
		})
	}
}
