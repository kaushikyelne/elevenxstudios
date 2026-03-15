package repository

import (
	"context"
	"database/sql"
	"errors"
	"time"

	"github.com/google/uuid"
	"github.com/lib/pq"

	"github.com/elevenxstudios/moneylane/services/notification/internal/domain"
)

// ErrDuplicate is returned when an event_id already exists.
var ErrDuplicate = errors.New("duplicate event_id")

// Repository defines the persistence interface.
type Repository interface {
	Insert(ctx context.Context, n *domain.Notification) error
	UpdateStatus(ctx context.Context, eventID string, status string) error
}

// PostgresRepository implements Repository using database/sql.
type PostgresRepository struct {
	db *sql.DB
}

// NewPostgresRepository creates a new PostgresRepository.
func NewPostgresRepository(db *sql.DB) *PostgresRepository {
	return &PostgresRepository{db: db}
}

// Insert persists a notification. Returns ErrDuplicate on UNIQUE violation.
func (r *PostgresRepository) Insert(ctx context.Context, n *domain.Notification) error {
	_, err := r.db.ExecContext(ctx,
		`INSERT INTO notifications (id, event_id, email, event_type, status, created_at)
		 VALUES ($1, $2, $3, $4, $5, $6)`,
		n.ID, n.EventID, n.Email, n.EventType, n.Status, n.CreatedAt,
	)
	if err != nil {
		// Check for unique constraint violation (PostgreSQL error code 23505)
		var pqErr *pq.Error
		if errors.As(err, &pqErr) && pqErr.Code == "23505" {
			return ErrDuplicate
		}
		return err
	}
	return nil
}

// UpdateStatus updates the status of a notification by event_id.
func (r *PostgresRepository) UpdateStatus(ctx context.Context, eventID string, status string) error {
	_, err := r.db.ExecContext(ctx,
		`UPDATE notifications SET status = $1 WHERE event_id = $2`,
		status, eventID,
	)
	return err
}

// RunMigrations executes the SQL migration file content against the database.
func RunMigrations(db *sql.DB, migrationSQL string) error {
	_, err := db.Exec(migrationSQL)
	return err
}

// NewNotification creates a Notification with generated UUID and current timestamp.
func NewNotification(event domain.NotificationEvent) *domain.Notification {
	return &domain.Notification{
		ID:        uuid.New(),
		EventID:   event.EventID,
		Email:     event.Email,
		EventType: event.EventType,
		Status:    domain.StatusPending,
		CreatedAt: time.Now().UTC(),
	}
}
