# Enterprise Purple Team Validation & Detection Coverage Platform

An enterprise-grade Purple Team platform for automated adversary emulation, SIEM detection validation, MITRE ATT&CK coverage evaluation, and detection gap analysis.

## Architecture Overview

Built with **Clean Architecture** principles:
- **API Layer**: FastAPI routes with type-safe Pydantic schemas
- **Service Layer**: Business logic with no dependencies on frameworks
- **Repository Layer**: Data access abstraction
- **Domain Models**: SQLAlchemy ORM with type hints
- **Integrations**: Isolated, pluggable tool integrations
- **Workers**: Async tasks via Celery

**Tech Stack**:
- Backend: Python 3.12, FastAPI, SQLAlchemy 2.0, Celery
- Database: PostgreSQL with async support
- Cache: Redis
- Infrastructure: Docker Compose

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)
- Git

### 1. Clone Repository

```bash
git clone https://github.com/Akhilesh-kolli/Enterprise-Purple-Team-Validation-Platform.git
cd Enterprise-Purple-Team-Validation-Platform
```

### 2. Environment Setup

```bash
# Copy example environment
cp .env.example .env

# For development, default values in .env should work
# For production, change JWT_SECRET_KEY and update credentials
```

### 3. Start Services (Docker Compose)

```bash
# Start all services (PostgreSQL, Redis, FastAPI, Celery)
docker-compose up -d

# Verify all services are running
docker-compose ps
```

**Services Running**:
- FastAPI Backend: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- pgAdmin: http://localhost:5050 (optional)

### 4. Initialize Database & Seed Data

```bash
# Option A: Using Docker Compose
docker-compose exec backend python scripts/seed_data.py

# Option B: Local Python (requires venv setup)
python scripts/seed_data.py
```

**Default Users Created**:
- **admin** / AdminPassword123 (ADMIN role)
- **purple_team_user** / TestPassword123 (PURPLE_TEAM role)
- **soc_analyst** / TestPassword123 (SOC_ANALYST role)
- **detection_eng** / TestPassword123 (DETECTION_ENGINEER role)
- **read_only_user** / TestPassword123 (READ_ONLY role)

### 5. Test the API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPassword123"}'

# Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}

# Refresh token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token_here>"}'
```

### 6. View API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Local Development (Without Docker)

### 1. Setup Python Virtual Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Ensure PostgreSQL is running locally on localhost:5432
# Create database manually or update DATABASE_URL in .env

# Copy .env.example to .env and update if needed
cp ../.env.example .env
```

### 3. Run Migrations (when ready - Phase 1)

```bash
# Setup Alembic (placeholder for now)
# alembic upgrade head
```

### 4. Seed Initial Data

```bash
python scripts/seed_data.py
```

### 5. Start FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Start Celery Worker (Optional)

```bash
# Requires Redis running on localhost:6379
celery -A app.celery_app worker --loglevel=info
```

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database connection
│   │   ├── dependencies.py      # Dependency injection
│   │   ├── logging.py           # Structured logging
│   │   └── celery_app.py        # Celery configuration
│   ├── api/
│   │   └── v1/
│   │       ├── routes/          # API endpoint handlers
│   │       │   ├── auth.py      # Authentication
│   │       │   └── health.py    # Health checks
│   │       └── schemas/         # Pydantic request/response models
│   ├── domain/
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── repositories/        # Data access layer
│   │   └── services/            # Business logic
│   ├── integrations/            # External tool integrations (Phase 3+)
│   ├── workers/                 # Celery async tasks (Phase 3+)
│   ├── utils/
│   │   ├── exceptions.py        # Custom exceptions
│   │   └── security.py          # JWT, password hashing
│   ├── tests/                   # Unit & integration tests
│   └── requirements.txt          # Python dependencies
├── frontend/                     # React/TypeScript (Phase 9)
├── docker/
│   ├── Dockerfile.backend       # Backend container image
│   └── Dockerfile.frontend      # Frontend container image (Phase 9)
├── docker-compose.yml           # Multi-container orchestration
├── scripts/
│   ├── seed_data.py            # Initial data seeding
│   └── ...                       # Additional scripts
├── docs/                         # Documentation
├── configs/                      # Configuration files
├── .gitignore                    # Git ignore rules
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

---

## Authentication & Authorization

### JWT Tokens

- **Access Token**: Short-lived (30 min), used for API requests
- **Refresh Token**: Long-lived (7 days), used to get new access token
- **Token Type**: Bearer

### Roles & Permissions

| Role | Permissions |
|------|-------------|
| **ADMIN** | Full system access, user management, settings |
| **PURPLE_TEAM** | Execute attacks, view all results |
| **SOC_ANALYST** | View alerts, incidents, dashboards |
| **DETECTION_ENGINEER** | Manage detection rules, view coverage |
| **READ_ONLY** | View-only access to dashboards |

### Header Format

```
Authorization: Bearer <access_token>
```

---

## API Endpoints (Phase 1)

### Authentication

- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/register` - Register new user (READ_ONLY role)
- `POST /api/v1/auth/refresh` - Refresh access token

### Health & Status

- `GET /api/v1/health` - System health (database, Redis, version)

### Asset Management (Phase 4)

- `GET /api/v1/assets` - List all assets
- `GET /api/v1/assets/{id}` - Get asset details
- `POST /api/v1/assets` - Create asset
- `PUT /api/v1/assets/{id}` - Update asset
- `DELETE /api/v1/assets/{id}` - Delete asset

### Attack Execution (Phase 5)

- `GET /api/v1/executions` - List executions
- `GET /api/v1/executions/{id}` - Get execution details
- `POST /api/v1/executions` - Create and start execution
- `DELETE /api/v1/executions/{id}` - Delete execution
- `GET /api/v1/executions/latest` - Latest execution updates (for polling)

---

## Database Schema (Phase 1)

### users
- id (PK)
- username (unique, indexed)
- email (unique, indexed)
- full_name
- hashed_password
- role (enum: admin, purple_team, soc_analyst, detection_engineer, read_only)
- is_active
- is_superuser
- created_at, updated_at

### audit_logs
- id (PK)
- user_id (FK)
- action
- resource_type
- resource_id
- details
- ip_address
- user_agent
- status
- created_at, updated_at

---

## Testing

### Run Tests

```bash
# Unit tests
pytest backend/tests/unit -v --cov=backend

# Integration tests
pytest backend/tests/integration -v

# All tests with coverage
pytest backend/tests -v --cov=backend --cov-report=html
```

### Test Coverage

- Target: 70%+ coverage
- Focus areas: Services, repositories, utilities

---

## Logging

Structured JSON logging using `structlog`:

```python
from app.logging import get_logger

logger = get_logger(__name__)
logger.info("event_name", key1="value1", key2="value2")
```

**Log Output** (production):
```json
{"event": "event_name", "key1": "value1", "key2": "value2", "timestamp": "2024-01-09T10:00:00Z"}
```

---

## Security Considerations

### Secrets Management
- **Never commit `.env`** to version control
- Always use `.env.example` as template
- Change `JWT_SECRET_KEY` in production
- Use strong database and Redis passwords

### Password Hashing
- Argon2 with tuned parameters
- Salting: automatic via Passlib

### HTTPS
- Production: Enable HTTPS via Nginx reverse proxy
- Development: HTTP is acceptable

---

## Phase 1 Completion Checklist

- [x] Project folder structure
- [x] Docker Compose environment
- [x] PostgreSQL database setup
- [x] FastAPI skeleton
- [x] User model with RBAC
- [x] JWT authentication (login, refresh)
- [x] Structured logging
- [x] Health check endpoint
- [x] Admin user seeding script
- [x] Environment variables
- [x] Requirements.txt
- [x] README with setup instructions

---

## Next Steps (Phase 2)

**Asset Management**:
- CRUD APIs for assets
- Asset types (server, workstation, DC, firewall, cloud)
- Asset search & filtering
- Bulk CSV import
- Agent tracking

---

## Contributing

1. Create feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m "feat: description"`
3. Push to branch: `git push origin feature/your-feature`
4. Create Pull Request

## License

Enterprise License - Internal Use Only

## Support

For issues, questions, or feature requests, contact the Security Architecture team.

---

**Last Updated**: 2026-07-09
**Phase**: 1 - Complete
**Status**: Ready for Phase 2.
