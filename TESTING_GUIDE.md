# Phase 1 Testing & Deployment Guide

## Quick Deployment (Docker Compose)

### Step 1: Start All Services

```bash
cd Enterprise-Purple-Team-Validation-Platform
docker-compose up -d
```

**Expected Output**:
```
Creating network "enterprise-purple-team-validation-platform_purple-team-network" with driver "bridge"
Creating purple-team-db ... done
Creating purple-team-redis ... done
Creating purple-team-backend ... done
Creating purple-team-celery ... done
Creating purple-team-pgadmin ... done
```

### Step 2: Verify Services Are Running

```bash
docker-compose ps
```

**Expected Output** (all RUNNING):
```
NAME                COMMAND                  SERVICE      STATUS      PORTS
purple-team-backend   "uvicorn app.main:..."  backend      Up 2 min    0.0.0.0:8000->8000/tcp
purple-team-celery    "celery -A app.celer..."celery       Up 2 min
purple-team-db        "docker-entrypoint.s..." postgres    Up 2 min    0.0.0.0:5432->5432/tcp
purple-team-redis     "redis-server"           redis       Up 2 min    0.0.0.0:6379->6379/tcp
purple-team-pgadmin   "/entrypoint.sh"         pgadmin     Up 2 min    0.0.0.0:5050->80/tcp
```

### Step 3: Seed Initial Data

```bash
docker-compose exec backend python scripts/seed_data.py
```

**Expected Output**:
```
✓ admin user created
✓ test_user_created (purple_team)
✓ test_user_created (soc_analyst)
✓ test_user_created (detection_engineer)
✓ test_user_created (read_only)
```

## API Testing

### Test 1: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Expected Response** (200 OK):
```json
{
  "status": "healthy",
  "database": "healthy",
  "redis": "healthy",
  "version": "1.0.0"
}
```

### Test 2: Admin Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "AdminPassword123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Test 3: Invalid Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "WrongPassword"
  }'
```

**Expected Response** (401 Unauthorized):
```json
{
  "detail": "Invalid username or password"
}
```

### Test 4: Refresh Token

```bash
# First get tokens from login
TOKEN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "AdminPassword123"}')

REFRESH_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.refresh_token')

# Use refresh token to get new access token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}"
```

**Expected Response** (200 OK):
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Test 5: User Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@localhost",
    "full_name": "New User",
    "password": "SecurePassword123"
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": 6,
  "username": "newuser",
  "email": "newuser@localhost",
  "full_name": "New User",
  "role": "read_only",
  "is_active": true,
  "created_at": "2024-01-09T10:00:00Z"
}
```

### Test 6: Duplicate Registration

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@localhost",
    "password": "Password123"
  }'
```

**Expected Response** (409 Conflict):
```json
{
  "detail": "User admin already exists"
}
```

## API Documentation

### Interactive Swagger UI
```
http://localhost:8000/docs
```

### ReDoc Documentation
```
http://localhost:8000/redoc
```

## Database Management

### Access pgAdmin
```
http://localhost:5050
```

**Credentials**:
- Email: admin@localhost
- Password: admin

**Add PostgreSQL Server**:
1. Right-click "Servers" → Create → Server
2. Name: "Purple Team DB"
3. Connection tab:
   - Host: postgres
   - Port: 5432
   - Username: admin
   - Password: password

### Direct psql Access

```bash
docker-compose exec postgres psql -U admin -d purple_team
```

**Useful Queries**:
```sql
-- View all users
SELECT id, username, email, role, is_active FROM users;

-- View audit logs
SELECT user_id, action, resource_type, status, created_at FROM audit_logs ORDER BY created_at DESC LIMIT 10;

-- Count tables
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';
```

## Logs Inspection

### Backend Logs
```bash
docker-compose logs -f backend
```

### Celery Worker Logs
```bash
docker-compose logs -f celery-worker
```

### PostgreSQL Logs
```bash
docker-compose logs -f postgres
```

### All Logs
```bash
docker-compose logs -f
```

## Testing Test Users

### Purple Team User
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "purple_team_user", "password": "TestPassword123"}'
```

### SOC Analyst User
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "soc_analyst", "password": "TestPassword123"}'
```

### Detection Engineer User
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "detection_eng", "password": "TestPassword123"}'
```

### Read Only User
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "read_only_user", "password": "TestPassword123"}'
```

## System Diagnostics

### Check Backend Connectivity
```bash
curl -v http://localhost:8000/
```

### Check PostgreSQL Connectivity
```bash
docker-compose exec backend python -c "
import asyncio
from app.database import engine
async def check():
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('✓ PostgreSQL connected')
asyncio.run(check())
"
```

### Check Redis Connectivity
```bash
docker-compose exec redis redis-cli PING
```

### Check Celery Connection
```bash
docker-compose exec backend celery -A app.celery_app inspect active
```

## Performance Testing

### Load Test Health Endpoint
```bash
# Install Apache Bench (ab)
ab -n 100 -c 10 http://localhost:8000/api/v1/health
```

### Load Test Login Endpoint
```bash
ab -n 100 -c 5 -p login.json -T application/json http://localhost:8000/api/v1/auth/login
```

(Create login.json with: `{"username":"admin","password":"AdminPassword123"}`)

## Troubleshooting

### Container Not Starting

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Port already in use: Change port in docker-compose.yml
# 2. Database not ready: Wait 10 seconds and retry
# 3. Missing .env: Copy .env.example to .env
```

### Database Connection Errors

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
sleep 10
docker-compose up -d
```

### Redis Connection Errors

```bash
# Check Redis
docker-compose exec redis redis-cli INFO server

# Restart Redis
docker-compose restart redis
```

### Permission Errors

```bash
# Linux/Mac: May need sudo
sudo docker-compose up -d

# Windows: Run PowerShell as Administrator
```

## Cleanup

### Stop All Services
```bash
docker-compose down
```

### Remove All Containers & Volumes (Full Reset)
```bash
docker-compose down -v
```

### Remove All Docker Resources (Dangerous)
```bash
docker system prune -a
```

## Success Checklist

After completing all tests, verify:

- ✅ All Docker containers are running
- ✅ Health check returns "healthy"
- ✅ Admin login returns valid JWT tokens
- ✅ Token refresh works
- ✅ New user registration works
- ✅ Duplicate registration returns 409 error
- ✅ PostgreSQL accessible via pgAdmin
- ✅ Logs visible in Docker Compose output
- ✅ Audit logs recorded for all actions
- ✅ API docs available at /docs

## Next Steps

Once all tests pass:

1. **Review Phase 1 Code**: Verify architecture patterns
2. **Plan Phase 2**: Asset Management CRUD
3. **Database Schema**: Prepare asset models
4. **APIs**: Design asset endpoints

---

**Testing completed**: Document evidence here
**Status**: Ready for Phase 2
**Issues found**: (Document any issues and fixes)

---

For questions or issues, refer to README.md
