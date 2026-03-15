package service

import (
	"context"
	"errors"
	"log/slog"
	"time"

	"github.com/elevenxstudios/moneylane/services/notification/internal/domain"
	"github.com/elevenxstudios/moneylane/services/notification/internal/email"
	"github.com/elevenxstudios/moneylane/services/notification/internal/repository"
)

const (
	maxRetries  = 3
	sendTimeout = 5 * time.Second
)

// NotificationService orchestrates notification processing.
type NotificationService struct {
	repo   repository.Repository
	sender email.Sender
	logger *slog.Logger
}

// NewNotificationService creates a new NotificationService.
func NewNotificationService(repo repository.Repository, sender email.Sender, logger *slog.Logger) *NotificationService {
	return &NotificationService{
		repo:   repo,
		sender: sender,
		logger: logger,
	}
}

// Process handles a notification event with idempotency and retry.
//
// Flow:
//  1. Try INSERT (status=PENDING) — UNIQUE constraint catches dupes
//  2. If duplicate → return "already_processed"
//  3. Retry send (max 3, 5s timeout each)
//  4. Update status = SENT or FAILED
//  5. Return response status
func (s *NotificationService) Process(ctx context.Context, event domain.NotificationEvent) string {
	start := time.Now()

	// Create notification record with internally generated UUID
	notification := repository.NewNotification(event)

	// INSERT-first — let DB constraint handle idempotency
	if err := s.repo.Insert(ctx, notification); err != nil {
		if errors.Is(err, repository.ErrDuplicate) {
			s.logger.Info("duplicate event",
				"event_id", event.EventID,
				"status", "already_processed",
				"latency_ms", time.Since(start).Milliseconds(),
			)
			return "already_processed"
		}
		s.logger.Error("failed to insert notification",
			"event_id", event.EventID,
			"error", err,
			"latency_ms", time.Since(start).Milliseconds(),
		)
		return "failed"
	}

	// Resolve email content based on event type
	subject, body := resolveEmailContent(event)

	// Retry send — simple for loop, no framework
	var sendErr error
	for i := 0; i < maxRetries; i++ {
		sendCtx, cancel := context.WithTimeout(ctx, sendTimeout)
		sendErr = s.sender.Send(sendCtx, event.Email, subject, body)
		cancel()

		if sendErr == nil {
			break
		}

		s.logger.Warn("send attempt failed",
			"event_id", event.EventID,
			"attempt", i+1,
			"error", sendErr,
		)
	}

	// Update status based on result
	if sendErr != nil {
		_ = s.repo.UpdateStatus(ctx, event.EventID, domain.StatusFailed)
		s.logger.Error("notification failed after retries",
			"event_id", event.EventID,
			"status", "failed",
			"latency_ms", time.Since(start).Milliseconds(),
			"error", sendErr,
		)
		return "failed"
	}

	_ = s.repo.UpdateStatus(ctx, event.EventID, domain.StatusSent)
	s.logger.Info("notification sent",
		"event_id", event.EventID,
		"status", "sent",
		"latency_ms", time.Since(start).Milliseconds(),
	)
	return "sent"
}

// resolveEmailContent maps event types to email subject and body.
func resolveEmailContent(event domain.NotificationEvent) (string, string) {
	switch event.EventType {
	case "WAITLIST_JOINED":
		name := event.Metadata["name"]
		if name == "" {
			name = "there"
		}
		subject := "Welcome to MoneyLane!"
		body := "Hey " + name + ",\n\nYou're on the waitlist! We'll notify you when we launch.\n\n— MoneyLane Team"
		return subject, body
	default:
		return "Notification from MoneyLane", "You have a new notification from MoneyLane."
	}
}
