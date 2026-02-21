# cph-da

Full-stack scaffold with:
- `backend/`: FastAPI + SQLAlchemy + Pydantic + Alembic
- `frontend/`: React + Vite with document selection, interview, outline, and export flows

## Deployment (VPS with Docker Compose)

1. Copy the example environment file and set secure secrets:
   ```bash
   cp .env.example .env
   ```
2. Build and start everything in the background:
   ```bash
   docker compose up -d --build
   ```
3. Check service status and logs:
   ```bash
   docker compose ps
   docker compose logs -f backend
   ```

### Migrations

- Migrations run automatically in the backend container entrypoint before the API starts.
- To run migrations manually:
  ```bash
  docker compose exec backend alembic upgrade head
  ```

### Backups

- Postgres data is persisted in the named volume `postgres_data`.
- Create a dump:
  ```bash
  docker compose exec -T postgres pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup.sql
  ```
- Restore from a dump:
  ```bash
  cat backup.sql | docker compose exec -T postgres psql -U "$POSTGRES_USER" "$POSTGRES_DB"
  ```
- Also back up the `app_storage` volume if your deployment writes user files there.
