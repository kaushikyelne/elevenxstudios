package main

import (
	"database/sql"
	"fmt"
	"log/slog"
	"net/http"
	"os"

	_ "github.com/lib/pq"

	"github.com/elevenxstudios/moneylane/services/notification/internal/email"
	"github.com/elevenxstudios/moneylane/services/notification/internal/handler"
	"github.com/elevenxstudios/moneylane/services/notification/internal/repository"
	"github.com/elevenxstudios/moneylane/services/notification/internal/service"
)

func main() {
	logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))

	// --- Config from env ---
	port := getEnv("PORT", "8080")
	dbURL := requireEnv("DATABASE_URL")
	brevoKey := requireEnv("BREVO_API_KEY")
	fromEmail := getEnv("FROM_EMAIL", "noreply@elevenxstudios.com")

	// --- Database ---
	db, err := sql.Open("postgres", dbURL)
	if err != nil {
		logger.Error("failed to connect to database", "error", err)
		os.Exit(1)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		logger.Error("failed to ping database", "error", err)
		os.Exit(1)
	}

	// --- Run migrations ---
	migrationSQL, err := os.ReadFile("migrations/001_create_notifications.sql")
	if err != nil {
		logger.Error("failed to read migration file", "error", err)
		os.Exit(1)
	}
	if err := repository.RunMigrations(db, string(migrationSQL)); err != nil {
		logger.Error("failed to run migration", "error", err)
		os.Exit(1)
	}
	logger.Info("database migration completed")

	// --- Wire dependencies ---
	repo := repository.NewPostgresRepository(db)
	sender := email.NewBrevoSender(brevoKey, fromEmail, "MoneyLane")
	svc := service.NewNotificationService(repo, sender, logger)
	h := handler.NewHandler(svc, logger)

	// --- HTTP server ---
	mux := http.NewServeMux()
	h.RegisterRoutes(mux)

	addr := fmt.Sprintf(":%s", port)
	logger.Info("starting notification service", "addr", addr)

	if err := http.ListenAndServe(addr, mux); err != nil {
		logger.Error("server failed", "error", err)
		os.Exit(1)
	}
}

func getEnv(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func requireEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		fmt.Fprintf(os.Stderr, "FATAL: required env var %s is not set\n", key)
		os.Exit(1)
	}
	return v
}
