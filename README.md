# Scalable Multi-Tenant Task & Analytics Platform

A production-ready, multi-tenant task management system built with Django, featuring real-time analytics, background job processing, and horizontal scalability.

## Architecture Overview

### Multi-Tenancy Implementation
**Choice: Schema-based multi-tenancy using django-tenants**

**Justification:**
- **Data Isolation:** Each tenant has a separate PostgreSQL schema, ensuring complete data isolation
- **Performance:** No row-level filtering overhead in queries
- **Security:** Impossible for tenants to access each other's data
- **Scalability:** Can shard tenants across multiple database servers if needed
- **Maintenance:** Easier schema migrations per tenant

**Tradeoffs:**
- More complex database management
- Cannot easily query across tenants
- Higher storage overhead per tenant

### Tech Stack
- **Backend:** Django 5.2 + Django REST Framework
- **Database:** PostgreSQL with schema-based multi-tenancy
- **Cache/Queue:** Redis (caching + rate limiting + Celery broker)
- **Async Jobs:** Celery + Redis
- **Frontend:** Django Templates + Bootstrap (simple but functional)
- **API Documentation:** OpenAPI/Swagger via drf-yasg

### Domain Model
- **Tenant:** Organization with isolated data
- **User:** RBAC (Admin/Manager/Member) with tenant association
- **Project:** Container for tasks within a tenant
- **Task:** Core entity with lifecycle (OPEN → IN_PROGRESS → BLOCKED → DONE)
- **TaskActivity:** Immutable audit log for all task changes
- **TaskSLA:** Time tracking per status for SLA monitoring
- **AnalyticsSnapshot:** Daily pre-aggregated analytics per project

## Key Features

### Business Logic
- **RBAC:** Role-based access control with granular permissions
- **Task Lifecycle:** Strict state transitions with validation
- **Soft Deletes:** Tasks marked as deleted, not removed
- **Audit Logs:** Complete history of all task changes
- **SLA Tracking:** Time spent in each status automatically calculated
- **Idempotent APIs:** Safe retry operations

### Advanced Features
- **Background Jobs:** Status changes trigger analytics updates and notifications
- **Daily Analytics:** Pre-aggregated snapshots for performance
- **Rate Limiting:** Per-tenant Redis-based rate limiting
- **Caching:** Redis caching for frequently accessed data

### API Design
- **RESTful:** Versioned APIs (/api/v1)
- **Proper HTTP Codes:** 200, 201, 400, 403, 404, etc.
- **OpenAPI:** Auto-generated documentation
- **Pagination:** Efficient large dataset handling
- **Filtering:** Query parameters for task filtering

## Scalability Strategy

### Current Architecture (10k-100k users)
- **Database:** Single PostgreSQL instance with schema isolation
- **Cache:** Redis for session storage, rate limiting, API caching
- **Queue:** Redis-backed Celery for background jobs
- **Web:** Gunicorn with multiple workers
- **Load Balancing:** Nginx for static files and request routing

### Scaling to 100k+ Users
1. **Database Sharding:**
   - Shard tenants across multiple PostgreSQL instances
   - Use tenant ID for shard routing
   - Maintain read replicas for analytics queries

2. **Caching Strategy:**
   - Redis Cluster for horizontal scaling
   - Cache analytics snapshots at application level
   - Cache user sessions and permissions

3. **Background Jobs:**
   - Multiple Celery workers with specialized queues
   - Priority queues for real-time vs batch operations
   - Dead letter queues for failed jobs

4. **Microservices Split (Future):**
   - Analytics service for heavy computations
   - Notification service for email/SMS
   - File storage service for attachments

5. **CDN & Static Assets:**
   - CloudFront/S3 for static files
   - Regional Redis caches

### Performance Optimizations
- **Pre-aggregated Analytics:** Daily snapshots avoid real-time calculations
- **Database Indexing:** Optimized queries with proper indexes
- **Connection Pooling:** PgBouncer for database connections
- **Async Operations:** Non-blocking background jobs

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Quick Start
```bash
# Clone repository
git clone <repo-url>
cd task-platform

# Start services
docker-compose up -d

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Load sample data
docker-compose exec web python manage.py load_sample_data
```

### Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Setup PostgreSQL and Redis
# Configure settings.py with your DB credentials

# Run migrations
python manage.py migrate

# Start Redis and Celery
redis-server
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info

# Start Django
python manage.py runserver
```

## API Usage

### Authentication
All API endpoints require authentication and tenant context.

**Headers:**
```
Authorization: Bearer <token>
X-Tenant-ID: <tenant-uuid>
```

### Sample API Calls

**List Tasks:**
```bash
GET /api/v1/tasks/?project=123
```

**Create Task:**
```bash
POST /api/v1/tasks/
{
  "project": 123,
  "title": "Implement user authentication",
  "description": "Add JWT authentication to the API"
}
```

**Update Task Status:**
```bash
PATCH /api/v1/tasks/456/
{
  "status": "IN_PROGRESS"
}
```

**Get Task Analytics:**
```bash
GET /api/v1/analytics/projects/123/
```

## Testing

### Unit Tests
```bash
python manage.py test tasks.tests.test_task_service
```

### API Tests
```bash
python manage.py test tasks.tests.test_api
```

### Load Testing
```bash
# Install locust
pip install locust

# Run load tests
locust -f load_tests.py
```

```bash
DATABASE_URL=postgres://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
CELERY_BROKER_URL=redis://host:6379/0
SECRET_KEY=your-secret-key
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60
```
