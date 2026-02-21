#!/usr/bin/env sh
set -eu

cd /app

echo "Running database migrations..."
until alembic upgrade head; do
  echo "Migration failed. Retrying in 3 seconds..."
  sleep 3
done

echo "Starting backend service..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
