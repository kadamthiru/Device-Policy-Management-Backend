# Device Policy Management Backend

A production-oriented backend system built using Django, Celery, Redis, and PostgreSQL to model how enterprise device policies are versioned, applied, and safely rolled back under concurrent administrative operations.

This project focuses on backend correctness, immutability, transactional consistency, and operational safety inspired by real-world Mobile Device Management (MDM) systems.

---

# Core Features

- Immutable policy versioning system
- Safe policy rollback mechanism
- Concurrent admin operation protection
- Async device policy application using Celery
- Row-level locking for transactional consistency
- Execution audit trail for policy assignments
- Retry orchestration with failure recovery
- Service-layer architecture for business logic isolation
- Dockerized local development environment

---

# Problem Statement

In enterprise environments, device policies change frequently and must be applied reliably across thousands of devices.

Common backend challenges include:

- Concurrent policy modifications from multiple administrators
- Rollback safety during failed deployments
- Ensuring devices always receive the correct active configuration
- Avoiding inconsistent state during worker or network failures
- Maintaining auditability for every execution attempt

This project addresses these problems at the backend systems level.

---

# System Architecture

```text
                    +----------------------+
                    |    Admin / Client    |
                    +----------+-----------+
                               |
                               v
                    +----------------------+
                    |    Django REST API   |
                    +----------+-----------+
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
    +-------------------+          +----------------------+
    |   PostgreSQL DB   |          |     Redis Queue      |
    | Policies + State  |          +-----------+----------+
    +-------------------+                      |
                                               v
                                   +----------------------+
                                   |    Celery Workers    |
                                   +-----------+----------+
                                               |
                                               v
                                   +----------------------+
                                   | PolicyExecutionJobs  |
                                   +----------------------+
```

---

# Policy Version Lifecycle

```text
ACTIVE_VERSION
       |
       v
CREATE NEW VERSION
       |
       v
ASSIGN TO DEVICES
       |
       v
ROLLBACK IF NEEDED
       |
       v
RESTORE PREVIOUS VERSION
```

---

# Execution Workflow

1. Admin creates a policy through the REST API.
2. Policy versions are stored as immutable records.
3. Devices are assigned policies through async jobs.
4. Celery workers consume assignment jobs from Redis queue.
5. Execution attempts are tracked in `PolicyExecutionJob`.
6. Failures trigger retries with exponential backoff.
7. Rollback operations restore a previous active version atomically.
8. Database transactions guarantee a single active version at all times.

---

# Core Design Principles

## Immutable Policy Versions

Policies act as logical containers while every configuration change creates a new immutable version.

This prevents:
- In-place mutation
- Configuration drift
- Unsafe concurrent updates

Benefits:
- Historical traceability
- Safer rollback operations
- Predictable system behavior

---

## Deterministic Rollback

Any previous policy version can be restored safely.

Rollback process:
- Previous version becomes active
- Devices are reassigned asynchronously
- Policy state remains transactionally consistent

The system guarantees:
- Only one active version exists at any time
- Rollback operations remain atomic

---

## Concurrency Safety

The system uses:
- PostgreSQL row-level locking (`select_for_update`)
- Atomic database transactions
- Serialized policy version updates

This prevents:
- Race conditions
- Duplicate active versions
- Concurrent rollback corruption

---

## Asynchronous Policy Application

Policy assignment operations are non-blocking and executed through Celery workers.

Benefits:
- Improved API responsiveness
- Retry-based failure recovery
- Observable execution state
- Worker-level scalability

---

# Key Challenges & Learnings

- Prevented race conditions where concurrent admin actions could create multiple active policy versions simultaneously.
- Ensured devices never resolved stale policy configurations during assignment workflows.
- Designed rollback workflows that maintain transactional consistency even under concurrent operations.
- Separated assignment state from execution attempts for improved auditability and debugging.

---

# Key Models

| Model | Responsibility |
|---|---|
| Policy | Logical policy container |
| PolicyVersion | Immutable configuration snapshot |
| Device | Managed enterprise device |
| DevicePolicyAssignment | Current device-policy relationship |
| PolicyExecutionJob | Async execution tracking and retries |

---

# API Endpoints

## Create Policy

```http
POST /api/policies/
```

---

## Create Policy Version

```http
POST /api/policies/{policy_id}/versions/
```

---

## Rollback Policy Version

```http
POST /api/policies/{policy_id}/rollback/{version_id}/
```

---

## Register Device

```http
POST /api/devices/
```

---

## Assign Policy To Device

```http
POST /api/devices/{device_id}/assign-policy/{policy_id}/
```

---

# Tech Stack

| Component | Technology |
|---|---|
| Backend Framework | Django, Django REST Framework |
| Async Processing | Celery |
| Queue Broker | Redis |
| Database | PostgreSQL |
| Containerization | Docker, Docker Compose |
| Language | Python |

---

# Project Structure

```text
device-policy-management-backend/
│
├── .github/
│   └── workflows/
│
├── assignments/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── base/
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── devices/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── jobs/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tasks.py
│   ├── tests.py
│   └── views.py
│
├── policies/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .gitignore
├── README.md
├── docker-compose.yml
├── main.py
├── manage.py
├── pyproject.toml
└── uv.lock
```

---

# Local Development Setup

## Prerequisites

- Docker
- Docker Compose

---

## Start Services

```bash
docker compose up --build
```

---

# Running Migrations

```bash
docker compose exec web python manage.py migrate
```

---

# Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

---

# Services

| Service | Description |
|---|---|
| web | Django API server |
| postgres | PostgreSQL database |
| redis | Redis message broker |
| celery-worker | Background task workers |

---

# Example Environment Variables

```env
DEBUG=True

POSTGRES_DB=policydb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

REDIS_URL=redis://redis:6379/0
```

---

# Reliability Patterns Implemented

- Immutable versioning
- Retry orchestration
- Transactional consistency
- Execution audit trails
- Failure recovery
- Async job queues
- Row-level locking
- Queue-based worker processing

---

# Future Improvements

- OpenAPI / Swagger documentation
- Prometheus metrics integration
- Distributed tracing
- Dead-letter queues
- Worker autoscaling
- Kubernetes deployment
- GitHub Actions CI pipeline

---

# Why This Project

This project is intentionally backend-focused and demonstrates:

- Backend system ownership
- Data integrity under concurrency
- Safe async processing
- Transactional consistency
- Production-oriented backend design decisions

---

# Author

Kadam Thirumalesh

GitHub:
https://github.com/kadamthiru
