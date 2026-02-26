# Production Readiness Plan

## 1. Current Architecture and Trust Boundaries
* **Architecture**: Next.js frontend, FastAPI backend, FastAPI demo-service, Prometheus/OTEL observability stack.
* **Trust Boundaries**: Currently, there are NO trust boundaries. All APIs are unauthenticated. The frontend communicates directly with the backend and demo-service without tokens.

## 2. API Endpoints and Access Requirements
* **Backend API (`/api/v1/*`)**: Needs Read-Only access for viewers, Read/Write for Operators.
* **Demo Service (`/api/experiments/*`)**: Highly sensitive. Requires Admin/Operator privileges. Currently unauthenticated.

## 3. Current Authentication & Authorization
* **Findings (CRITICAL)**: No authentication exists. No RBAC exists.
* **Plan**: Implement JWT Bearer token authentication. In production, this should integrate with an OIDC provider. For local dev, a static or locally-issued token mechanism will be explicitly separated.

## 4. Database Models and Migrations
* **Findings (HIGH)**: Defaulting to SQLite. Missing explicit PostgreSQL configuration, pooling, and timeout handling.
* **Plan**: Add `psycopg2-binary`, implement database URL parsing, configure SQLAlchemy connection pooling, and ensure Alembic works for PG. Fail startup if `DATABASE_URL` is missing in production.

## 5. Telemetry and Alerting Data Flow
* **Findings (MEDIUM)**: Relies on hardcoded targets. Missing platform-level self-monitoring health checks.
* **Plan**: Refine Prometheus scrape configs and OTEL collector pipelines to use environment variables and label standardizations.

## 6. Containers, Kubernetes, Helm, Terraform
* **Findings (HIGH)**: Containers might run as root if not strictly enforced in Dockerfiles. Helm secrets management needs review.
* **Plan**: Update Dockerfiles for non-root users. Add resource requests/limits in K8s/Helm. 

## 7. Frontend Integration
* **Findings (HIGH)**: Frontend silently falls back to mock data on API failure.
* **Plan**: Disable mock data fallback when `NODE_ENV === 'production'`. Implement global error boundaries and explicit unauthorized states.

## 8. Safe Resilience Experiments
* **Findings (CRITICAL)**: Fault injection endpoints in demo-service lack global kill switch and strict limits.
* **Plan**: Add a hard limit to latency (max 5000ms). Add a hard limit to error rate (max 1.0). Require an authorization header. Implement an emergency stop `DELETE /api/experiments`.

## Execution Phases
1. Security Hardening (Auth, CORS, Limits).
2. Database Reliability (PostgreSQL, Pooling).
3. Demo Service Safety (Auth on injection, Limits).
4. Frontend Strictness (No mocks in prod).
5. Infrastructure Hardening (Non-root, probes).
6. Testing and QA.
