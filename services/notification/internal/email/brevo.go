package email

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
)

const brevoAPIURL = "https://api.brevo.com/v3/smtp/email"

// Sender defines the interface for sending emails.
type Sender interface {
	Send(ctx context.Context, to, subject, body string) error
}

// BrevoSender implements Sender using the Brevo (formerly Sendinblue) API.
type BrevoSender struct {
	apiKey    string
	fromEmail string
	fromName  string
	client    *http.Client
}

// NewBrevoSender creates a new BrevoSender.
func NewBrevoSender(apiKey, fromEmail, fromName string) *BrevoSender {
	return &BrevoSender{
		apiKey:    apiKey,
		fromEmail: fromEmail,
		fromName:  fromName,
		client:    &http.Client{},
	}
}

// brevoRequest is the Brevo transactional email payload.
type brevoRequest struct {
	Sender      brevoContact   `json:"sender"`
	To          []brevoContact `json:"to"`
	Subject     string         `json:"subject"`
	HTMLContent string         `json:"htmlContent"`
}

type brevoContact struct {
	Email string `json:"email"`
	Name  string `json:"name,omitempty"`
}

// Send sends an email via the Brevo API. Respects context cancellation/timeout.
func (b *BrevoSender) Send(ctx context.Context, to, subject, body string) error {
	payload := brevoRequest{
		Sender:      brevoContact{Email: b.fromEmail, Name: b.fromName},
		To:          []brevoContact{{Email: to}},
		Subject:     subject,
		HTMLContent: body,
	}

	jsonBody, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("failed to marshal brevo request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, brevoAPIURL, bytes.NewReader(jsonBody))
	if err != nil {
		return fmt.Errorf("failed to create brevo request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("api-key", b.apiKey)

	resp, err := b.client.Do(req)
	if err != nil {
		return fmt.Errorf("brevo request failed: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		respBody, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("brevo returned status %d: %s", resp.StatusCode, string(respBody))
	}

	return nil
}
