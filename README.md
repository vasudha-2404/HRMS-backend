# PathVision HRMS Backend

Production-ready Human Resource Management System API built with **FastAPI**, **PostgreSQL (Supabase)**, **SQLAlchemy 2.0 (Async)**, **JWT Authentication**, and **RBAC**.

## Overview

**PathVision HRMS** is an enterprise-ready backend platform for managing complete HR operations:
- Employee lifecycle management
- Attendance and leave workflows
- Task assignment and reporting
- Recruitment ATS pipeline
- Notifications and analytics dashboards

The API is frontend-ready for:
- Flutter mobile app
- Flutter web app
- Admin dashboard
- Future microservices

## Why This Project Exists

As HR systems scale, backend complexity grows quickly. PathVision HRMS is designed to keep operations secure, maintainable, and extensible by using:
- Clean architecture with clear layer separation
- Async I/O for scalable API performance
- Strong authentication and role-based access control
- Consistent API contracts for frontend teams
- Docker-first deployment for predictable environments

## Request Lifecycle (High-Level Architecture)

1. Client sends request to `/api/v1/...`
2. Middleware processes request (CORS, logging, rate-limit hooks)
3. JWT token is validated and current user is resolved
4. RBAC checks role permissions for protected routes
5. Pydantic validates input payload and query parameters
6. Route calls service layer (business rules)
7. Service uses repository layer for database operations
8. SQLAlchemy async session executes PostgreSQL queries
9. Standard response is returned to client

## Tech Stack

| Component | Technology |
|---|---|
| API Framework | FastAPI |
| Runtime Server | Uvicorn |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy 2.0 Async |
| Migrations | Alembic |
| Auth | JWT + Refresh Tokens + Bcrypt |
| Validation | Pydantic v2 |
| Queue/Cache | Celery + Redis |
| Reverse Proxy | Nginx |
| Containerization | Docker + Docker Compose |

## Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── employees.py
│   │   │   ├── interns.py
│   │   │   ├── attendance.py
│   │   │   ├── leaves.py
│   │   │   ├── tasks.py
│   │   │   ├── recruitment.py
│   │   │   ├── dashboard.py
│   │   │   ├── notifications.py
│   │   │   └── health.py
│   │   └── api.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── logger.py
│   ├── middleware/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── notifications/
│   ├── utils/
│   ├── scripts/
│   └── main.py
├── alembic/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

## Quick Start (Windows + venv + uvicorn) 🚀

```powershell
cd "C:\HRM Backend\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API base URL: `http://127.0.0.1:8000/api/v1`

## Environment Variables

Create `.env` from `.env.example` and configure:

```env
APP_NAME=PathVision HRMS
APP_VERSION=1.0.0
ENVIRONMENT=development
DEBUG=true

API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000

DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@db.your-project.supabase.co:5432/postgres
DATABASE_SYNC_URL=postgresql://postgres:YOUR_PASSWORD@db.your-project.supabase.co:5432/postgres

SECRET_KEY=change-me-to-a-long-random-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

> Note: URL-encode special characters in passwords (`@` -> `%40`).

## API Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Core Modules

- `auth` - JWT login, refresh, logout, current user
- `employees` - employee profile and management APIs
- `interns` - intern and batch management
- `attendance` - check-in/out, GPS data, approvals
- `leaves` - apply/approve/reject leave workflows
- `tasks` - assignment, status updates, comments
- `recruitment` - job openings, applicants, interviews, ATS pipeline
- `notifications` - in-app notifications and read tracking
- `dashboard` - attendance, leave, task, ATS, employee analytics
- `health` - service health endpoint

## RBAC Roles

- `super_admin`
- `hr_admin`
- `team_lead`
- `employee`
- `intern`
- `reviewer`

## Standard API Response Format

Success:

```json
{
  "success": true,
  "message": "Success",
  "data": {}
}
```

Error:

```json
{
  "success": false,
  "error": "Error message"
}
```

## Security Features

- JWT access and refresh token flow
- Bcrypt password hashing
- RBAC guard dependencies on protected routes
- Input validation using Pydantic v2
- SQLAlchemy ORM protections against SQL injection
- Environment-based config management
- CORS middleware
- Logging middleware and centralized exception handling
- Rate-limiting ready middleware hooks
- Audit logging model for traceability

## Docker Deployment

```bash
cd backend
docker-compose up -d --build
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed_data.py
docker-compose logs -f api
```

Services included:
- FastAPI API
- PostgreSQL
- Redis
- Celery worker
- Nginx

## License

Proprietary - PathVision HRMS
