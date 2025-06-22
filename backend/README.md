Scheduler API — Back-end

A FastAPI + SQLModel back-end that powers a mini-Calendly web app:

Create public events with multiple time-slots
Visitors book slots in their own time-zone
E-mail confirmations + .ics + Google-Calendar link
Live WebSocket updates (no double-booking)
Ratings, search / filters, category & price sorting
S3 (or MinIO) upload for event branding images

Tech Stack
Layer	Choice & Why
Runtime	Python 3.12
Web	FastAPI (+ Uvicorn) ⟶ async, OpenAPI docs
ORM	SQLModel / SQLAlchemy 2
DB	PostgreSQL 16 (SQLite for tests)
Migrations	Alembic
Async tasks	Celery + Redis
Realtime	Redis pub/sub → FastAPI WebSocket
Object storage	S3 / MinIO
E-mail	Console | SES | SendGrid (via env flag)
Container	Multi-stage Dockerfile (+ docker-compose)
Tests	Pytest + TestClient (Celery eager)

cp backend/.env.example backend/.env   # edit secrets
docker compose -f backend/docker-compose.yml up --build

