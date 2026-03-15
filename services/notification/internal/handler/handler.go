package handler

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"strings"

	"github.com/elevenxstudios/moneylane/services/notification/internal/domain"
	"github.com/elevenxstudios/moneylane/services/notification/internal/service"
)

// Handler holds HTTP handlers for the notification service.
type Handler struct {
	svc    *service.NotificationService
	logger *slog.Logger
}

// NewHandler creates a new Handler.
func NewHandler(svc *service.NotificationService, logger *slog.Logger) *Handler {
	return &Handler{svc: svc, logger: logger}
}

// RegisterRoutes registers all HTTP routes on the given mux.
func (h *Handler) RegisterRoutes(mux *http.ServeMux) {
	mux.HandleFunc("POST /notifications/email", h.SendNotification)
	mux.HandleFunc("GET /notifications/health", h.HealthCheck)
}

// HealthCheck returns service health status.
func (h *Handler) HealthCheck(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

// SendNotification processes an incoming notification event.
func (h *Handler) SendNotification(w http.ResponseWriter, r *http.Request) {
	var event domain.NotificationEvent
	if err := json.NewDecoder(r.Body).Decode(&event); err != nil {
		h.respondJSON(w, http.StatusBadRequest, domain.NotificationResponse{Status: "invalid_request"})
		return
	}

	// Basic validation
	if err := validateEvent(event); err != nil {
		h.respondJSON(w, http.StatusBadRequest, domain.NotificationResponse{Status: err.Error()})
		return
	}

	status := h.svc.Process(r.Context(), event)

	switch status {
	case "sent":
		h.respondJSON(w, http.StatusOK, domain.NotificationResponse{Status: status})
	case "already_processed":
		h.respondJSON(w, http.StatusOK, domain.NotificationResponse{Status: status})
	default:
		h.respondJSON(w, http.StatusInternalServerError, domain.NotificationResponse{Status: status})
	}
}

func (h *Handler) respondJSON(w http.ResponseWriter, code int, data any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(data)
}

func validateEvent(e domain.NotificationEvent) error {
	if strings.TrimSpace(e.EventID) == "" {
		return errMissing("event_id")
	}
	if strings.TrimSpace(e.Email) == "" {
		return errMissing("email")
	}
	if strings.TrimSpace(e.EventType) == "" {
		return errMissing("event_type")
	}
	return nil
}

type validationError struct {
	field string
}

func (e *validationError) Error() string {
	return "missing_" + e.field
}

func errMissing(field string) error {
	return &validationError{field: field}
}
