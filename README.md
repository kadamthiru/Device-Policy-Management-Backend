# Device Policy Management Backend

A backend system that models how enterprise device policies are versioned, applied, and safely rolled back under concurrent administrative changes.

This project focuses on **correctness, immutability, and operational safety**, inspired by real-world MDM systems.

---

## Problem Statement

In enterprise environments, device policies change frequently and must be applied reliably across thousands of devices.  
Common challenges include:

- Policies being modified concurrently by multiple admins
- Needing to roll back bad configurations safely
- Ensuring devices always apply the correct configuration
- Avoiding partial or inconsistent state during failures

This project addresses these problems at the backend level.

---
## Key Challenges & Learnings

- Prevented race conditions where concurrent admin actions (e.g., version creation or rollback) could result in multiple active policy versions by enforcing row-level locking and transactional updates.
- Ensured devices never applied stale configurations by always resolving the current policy version inside a database transaction before assignment.

---

## Core Design Principles

### 1. Immutable Policy Versions
- Policies act as logical containers
- Configuration changes create new immutable versions
- No in-place mutation of policy data

### 2. Deterministic Rollback
- Any previous version can be restored
- Rollback re-applies configuration to all assigned devices
- Guarantees a single active version at all times

### 3. Concurrency Safety
- Row-level locking (`select_for_update`)
- Atomic transactions for version changes
- Prevents race conditions during concurrent updates

### 4. Asynchronous Policy Application
- Policy application is non-blocking
- Executed via Celery workers
- Retries and failures are observable

---

## Architecture Overview

- Django REST API (thin controllers)
- PostgreSQL for persistence
- Celery + Redis for background execution
- Service-layer business logic

---

## Key Models

- Policy
- PolicyVersion
- Device
- DevicePolicyAssignment
- PolicyExecutionJob

Each execution attempt is tracked for auditability and debugging.

---

## API Endpoints

- POST /api/policies/
- POST /api/policies/{policy_id}/versions/
- POST /api/policies/{policy_id}/rollback/{version_id}/
- POST /api/devices/
- POST /api/devices/{device_id}/assign-policy/{policy_id}/

---

## Failure Handling

- Async jobs retry on transient failures
- Assignment state persists independently of execution
- System remains consistent even if workers are down

---

## Why This Project

This project is intentionally backend-focused and demonstrates:
- System ownership
- Data integrity under concurrency
- Safe async processing
- Production-grade backend design decisions
