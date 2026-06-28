-- Initialise PostgreSQL schemas for CQRS write/read sides.
-- Runs automatically on first container start via docker-entrypoint-initdb.d.

CREATE SCHEMA IF NOT EXISTS chat_write;
CREATE SCHEMA IF NOT EXISTS chat_read;
CREATE SCHEMA IF NOT EXISTS plot_write;
CREATE SCHEMA IF NOT EXISTS plot_read;
