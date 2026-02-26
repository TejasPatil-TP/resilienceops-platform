# Architecture

## Core Components
1. **Frontend (Next.js)**
   Provides the UI for operators to view service health, SLO compliance, and to trigger resilience experiments. Communicates via REST with the Backend API.
2. **Backend API (FastAPI)**
   Manages the state of SLOs, error budgets, active experiments, and alerts. Persists data to an SQLite database (extensible to PostgreSQL).
3. **Demo Service (FastAPI)**
   A sample workload instrumented with OpenTelemetry. Contains specific endpoints (`/api/experiments/*`) designed to artificially inject latency and error rates to simulate degraded performance safely.
4. **Observability Stack**
   - **OpenTelemetry Collector**: Receives OTLP traces and metrics from the Demo Service, exporting them to Prometheus and Loki.
   - **Prometheus**: Scrapes metrics from the OTEL Collector and the Demo Service's `/metrics` endpoint directly.
   - **Loki**: Stores logs (if exported via OTEL).
   - **Grafana**: Visualizes metrics and logs.

## Data Flow (Metrics)
`Demo Service` -> `OpenTelemetry Collector` -> `Prometheus` -> `Grafana`

## Data Flow (Experiments)
`Frontend` -> `Backend API` -> (User tracks state)
`Frontend` -> `Demo Service` (Triggers fault injection directly for this local architecture, though a true control plane would have the Backend orchestrate this).
