# PathVision HRMS Backend

Production-ready Human Resource Management System API built with **FastAPI**, **PostgreSQL (Supabase)**, **SQLAlchemy 2.0**, **JWT Authentication**, and **RBAC**.

## Tech Stack

| Component | Technology |
|-----------|------------|
| API Framework | FastAPI |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Auth | JWT + Bcrypt |
| Cache/Queue | Redis + Celery |
| Proxy | Nginx |
| Container | Docker |

## Project Structure

```
backend/
├── app/
│   ├── api/routes/       # REST endpoints
│   ├── core/             # Config, DB, security, dependencies
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic validation
│   ├── services/         # Business logic
│   ├── repositories/     # Data access layer
│   ├── middleware/       # Logging, rate limit, exceptions
│   ├── notifications/    # Email-ready notifications
│   └── main.py           # Application entry
├── alembic/              # Database migrations
├── scripts/seed_data.py  # Sample seed data
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Quick Start (Local)

### 1. Prerequisites

- Python 3.12+
- PostgreSQL (or Supabase project)
- Redis (optional, for Celery)

### 2. Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Windows PowerShell Setup (Exact)

```powershell
cd "C:\HRM Backend\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Environment

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql+asyncpg://postgres:PASSWORD@host:5432/postgres
DATABASE_SYNC_URL=postgresql://postgres:PASSWORD@host:5432/postgres
SECRET_KEY=your-secret-key-min-32-chars
```

> **Note:** URL-encode special characters in passwords (`@` → `%40`).

### 4. Database Migrations

```bash
# Generate migration (after model changes)
alembic revision --autogenerate -m "initial"

# Apply migrations
alembic upgrade head
```

> This repo also includes a ready `0001_initial` migration in `alembic/versions/`.

### 5. Seed Data

```bash
python scripts/seed_data.py
```

**Default accounts:**
| Role | Email | Password |
|------|-------|----------|
| Super Admin | admin@pathvision.com | Admin@123 |
| HR Admin | hr@pathvision.com | Hr@12345 |

### 6. Run Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

| Resource | URL |
|----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |
| Health Check | http://localhost:8000/api/v1/health |

**Base URL:** `/api/v1`

### Response Format

```json
{
  "success": true,
  "message": "Success",
  "data": {}
}
```

### Error Format

```json
{
  "success": false,
  "error": "Error message"
}
```

## Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@pathvision.com","password":"Admin@123"}'

# Use token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

## API Modules

| Module | Prefix | Description |
|--------|--------|-------------|
| Auth | `/auth` | Login, register, refresh, logout, me |
| Employees | `/employees` | CRUD employee profiles |
| Attendance | `/attendance` | Check-in/out, GPS, approval |
| Leaves | `/leaves` | Apply, team lead & HR approval |
| Tasks | `/tasks` | Assign, comments, status |
| Recruitment | `/recruitment` | ATS, Kanban, interviews |
| Notifications | `/notifications` | In-app notifications |
| Dashboard | `/dashboard` | Analytics & metrics |
| Interns | `/interns` | Intern batches |

## Roles (RBAC)

- Super Admin
- HR Admin
- Team Lead
- Employee
- Intern
- Reviewer

## Docker Deployment

```bash
# Start all services
docker-compose up -d --build

# View logs
docker-compose logs -f api

# Run migrations inside container
docker-compose exec api alembic upgrade head

# Seed data
docker-compose exec api python scripts/seed_data.py
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| api | 8000 | FastAPI application |
| db | 5432 | PostgreSQL |
| redis | 6379 | Cache & Celery broker |
| celery | - | Background worker |
| nginx | 80 | Reverse proxy |

## Production Deployment

1. Set `ENVIRONMENT=production` and `DEBUG=false`
2. Use a strong `SECRET_KEY` (32+ random characters)
3. Configure Supabase connection with SSL
4. Run behind Nginx with HTTPS (Let's Encrypt)
5. Use managed Redis (ElastiCache, Upstash)
6. Set up CI/CD for migrations before deploy
7. Enable monitoring (Sentry, Datadog)
8. **Never commit `.env` with real credentials**

### Supabase Production URL

```
postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
```

## Flutter / Frontend Integration

- All endpoints return consistent `{ success, message, data }` JSON
- Pagination: `?page=1&page_size=20`
- Search: `?search=keyword`
- Sorting: `?sort_by=created_at&sort_order=desc`
- Auth header: `Authorization: Bearer <token>`

## Testing

```bash
pytest tests/ -v
```

## Database Tables

`users`, `roles`, `permissions`, `role_permissions`, `employees`, `departments`, `teams`, `interns`, `intern_batches`, `attendance`, `leaves`, `tasks`, `task_comments`, `reports`, `applicants`, `interviews`, `job_openings`, `notifications`, `activity_logs`, `documents`, `projects`

All tables use:
- UUID primary keys
- Soft deletes (`deleted_at`)
- Timestamps (`created_at`, `updated_at`)

## License

Proprietary - PathVision HRMS

