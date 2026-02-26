# ResilienceOps Platform

## 1. Project Introduction
ResilienceOps Platform is a comprehensive, cloud-native reliability engineering platform. It helps engineering teams observe services, measure service reliability, evaluate service-level objectives (SLOs), understand error-budget consumption, run controlled resilience experiments, and validate deployment health.

This platform provides a local-first working environment that operates without requiring paid cloud resources. It also includes well-documented optional infrastructure-as-code (IaC) examples for AWS, Azure, and Google Cloud Platform (GCP).
By shifting the focus from simple uptime pinging to genuine telemetry-based service-level indicators (SLIs), this tool enables teams to measure what truly matters: customer experience. It implements the core Site Reliability Engineering (SRE) principle that 100% reliability is the wrong target, providing actionable data on how and when to spend your remaining error budget on innovation or feature velocity.

## 2. Problem Statement and Target Audience
Modern microservices generate vast amounts of telemetry, but translating that raw data into actionable insights about reliability is challenging. Engineering teams struggle to answer critical questions:
- Are we meeting our reliability promises to customers?
- How much error budget is left for this deployment cycle?
- Will our system withstand a sudden spike in latency or a failure in a dependent service?
- Is our latest deployment genuinely healthy based on real telemetry, rather than just passing CI checks?

**Target Audience:**
- **Site Reliability Engineers (SREs):** To define SLOs, track error budgets, investigate burn rates, and run resilience tests.
- **Platform Engineers:** To deploy and maintain the observability and reliability control plane, ensuring standardized metrics across all internal services.
- **Software Developers:** To understand how their services behave under stress and verify deployment health during active development.
- **QA Engineers:** To run fault injection experiments and chaos tests against pre-production environments.
- **Engineering Managers:** To balance the trade-off between release velocity and stability using objective error budget data.

## 3. Feature Matrix
The following table outlines the current capabilities and maturity of the platform.

| Feature | Status | Description |
|---------|--------|-------------|
| Demo Service with Telemetry | Implemented | FastAPI service with OTEL tracing and Prometheus metrics. Includes mock endpoints for generating baseline traffic. |
| OpenTelemetry & Prometheus | Implemented | Local observability stack collecting real metrics via the OTEL Collector and scraping directly with Prometheus. |
| Grafana Dashboards | Implemented | Pre-provisioned dashboards for service health, request rates, error rates, and SLO compliance tracking. |
| SLO & Error Budget Engine | Implemented | Backend calculations for availability and burn rates based on time-window rolling data. |
| Safe Resilience Experiments | Implemented | Controlled latency and error injection via API. Operators can bound latency up to 5 seconds and error rates up to 100%. |
| Alert Management | Implemented | Detection and tracking of reliability events. Supports acknowledging and resolving critical alerts. |
| Next.js Dashboard UI | Implemented | Unified interface for viewing SLOs and running experiments. Includes service catalog and alert history. |
| Multi-Cloud Terraform | Implemented | IaC templates for AWS EKS, Azure AKS, and GCP GKE, utilizing official modules for secure deployments. |
| Helm Chart | Implemented | Kubernetes packaging for the platform, enabling easy configuration overrides and versioned deployments. |
| CI/CD Pipeline | Implemented | GitHub Actions workflow that executes tests, lints code, builds the Next.js frontend, and validates Terraform. |
| SSO/RBAC Integration | Planned | Single Sign-On and Role-Based Access Control for restricting resilience experiments to authorized users only. |

## 4. Architecture Overview
The platform consists of a modern frontend, a robust backend API, a sample workload (demo-service), and an observability stack (OpenTelemetry Collector, Prometheus, Grafana, Loki).

```mermaid
flowchart TD
    UI[Frontend (Next.js)] -->|REST API| API[Backend (FastAPI)]
    API <--> DB[(SQLite/PostgreSQL)]
    
    UI -->|Triggers| Exp[Resilience Experiments]
    Exp -.->|Injects Faults| Demo[Demo Service]
    
    Demo -->|Metrics| Prom[Prometheus]
    Demo -->|Traces/Logs| OTEL[OTEL Collector]
    
    OTEL -->|Metrics| Prom
    OTEL -->|Logs| Loki[Loki]
    
    Grafana[Grafana] -->|Queries| Prom
    Grafana -->|Queries| Loki
    
    API -.->|Reads metrics for SLOs| Prom
```

The architecture emphasizes loose coupling. The UI never talks directly to the database or telemetry systems, instead relying on the Backend API to act as the source of truth for SLO configurations and experiment states. The backend, in turn, polls Prometheus to evaluate SLOs on a scheduled basis, generating alerts if burn rates exceed thresholds.

## 5. Repository Structure
The repository is split into independent domains to allow modular development and clear ownership.

```text
resilienceops-platform/
├── frontend/           # Next.js React application with Tailwind CSS and Recharts
├── backend/            # FastAPI Python backend (SLO & Alert engine, SQLite DB)
├── demo-service/       # Instrumented sample FastAPI service with fault injection capabilities
├── observability/      # Configs for OTEL Collector, Prometheus, Grafana, and Loki
├── infrastructure/     # Docker Compose, Kubernetes manifests, Helm charts, Terraform examples
├── docs/               # Architecture diagrams, Security reviews, Operations runbooks
├── scripts/            # Helper scripts for local development and mock traffic generation
└── tests/              # End-to-end acceptance tests connecting all components
```

## 6. Technology Stack
The platform leverages industry-standard tools to ensure compatibility and ease of adoption.
- **Frontend:** Next.js (App Router), React, TypeScript, Tailwind CSS, Recharts, Lucide Icons.
- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, SQLite (with native support for PostgreSQL), Alembic for migrations, Pydantic for validation.
- **Demo Service:** Python 3.11+, FastAPI, OpenTelemetry SDK, Prometheus Client, HTTPX.
- **Observability:** OpenTelemetry Collector (Contrib), Prometheus (v2.50+), Grafana (v10.4+), Loki (v2.9+).
- **Infrastructure:** Docker, Docker Compose (v2), Kubernetes (v1.29+), Helm (v3), Terraform (v1.5+).
- **CI/CD:** GitHub Actions (Linting, Testing, Build verification, IaC validation).

## 7. Prerequisites
To run the platform locally, you will need the following tools installed on your machine:
- Docker Engine and Docker Compose (v2 or later).
- Python 3.11 or higher (if running services natively).
- Node.js 20 or higher (if running the frontend natively).
- Git for version control.
- `make` (Optional, for running convenient shortcuts on macOS/Linux).

## 8. Windows PowerShell Installation
If you are developing on a Windows machine, follow these steps to prepare your environment:
1. Install Docker Desktop for Windows. Ensure the WSL 2 backend is enabled for better performance.
2. Install Python 3.11 and Node.js. You can use winget:
   ```powershell
   winget install Python.Python.3.11
   winget install OpenJS.NodeJS
   ```
3. Open PowerShell and clone the repository:
   ```powershell
   git clone https://github.com/TejasPatil-TP/resilienceops-platform.git
   cd resilienceops-platform
   ```

## 9. macOS/Linux Installation
If you are developing on macOS or a Linux distribution, use your system package manager:
1. Install Docker, Python, and Node.js using Homebrew (macOS) or apt/dnf (Linux):
   ```bash
   brew install docker python@3.11 node
   ```
2. Clone the repository and navigate into the directory:
   ```bash
   git clone https://github.com/TejasPatil-TP/resilienceops-platform.git
   cd resilienceops-platform
   ```

## 10. Environment Variables
The platform relies on environment variables for configuration. Copy the `.env.example` file to `.env` in the root directory (if provided). If no `.env` file is present, the system defaults defined in `docker-compose.yml` will be used safely.
Key variables include:
- `NEXT_PUBLIC_API_URL`: The URL where the frontend expects to find the Backend API (default: `http://localhost:8000/api/v1`).
- `OTEL_EXPORTER_OTLP_ENDPOINT`: The endpoint for the OTEL collector (default: `http://otel-collector:4317`).
- `OTEL_SERVICE_NAME`: The name of the instrumented service (default: `demo-service`).
- `DATABASE_URL`: The SQLAlchemy connection string for the backend (default: `sqlite:///./resilienceops.db`).

## 11. Local Startup Instructions
You can start the entire stack using Docker Compose, or run the services individually for focused development.
To run individual services natively (without Docker):
1. Navigate to the `backend/` directory, create a virtual environment, install `requirements.txt`, and run `uvicorn app.main:app --port 8000`.
2. Navigate to the `demo-service/` directory, do the same, and run `uvicorn app.main:app --port 8080`.
3. Navigate to the `frontend/` directory, run `npm install`, and then `npm run dev`.

## 12. Docker Compose Usage
The recommended way to bring up the full platform is via Docker Compose.
```bash
# Using Make (macOS/Linux)
make up

# Using Docker Compose directly (Windows/macOS/Linux)
docker compose up -d
```
Once the containers have started, the services will be available at the following local URLs:
- Frontend Dashboard: `http://localhost:3000`
- Backend API Documentation (Swagger UI): `http://localhost:8000/docs`
- Demo Service API Documentation: `http://localhost:8080/docs`
- Grafana (Credentials: admin/admin): `http://localhost:3001`
- Prometheus Expression Browser: `http://localhost:9090`

## 13. API Reference and Example Requests
The backend exposes a versioned REST API at `/api/v1`. All endpoints accept and return JSON.
- `GET /api/v1/health`: Returns API health status.
- `GET /api/v1/services`: Lists all monitored services.
- `POST /api/v1/services`: Registers a new service.
  ```json
  { "name": "Payment Gateway", "version": "v1.2.0" }
  ```
- `GET /api/v1/slos`: Lists SLO configurations.
- `POST /api/v1/slos`: Creates a new SLO.
  ```json
  { "service_id": 1, "name": "Checkout Availability", "target_availability": 99.9, "window_days": 30 }
  ```
- `GET /api/v1/alerts`: Retrieves active system alerts.
- `POST /api/v1/experiments`: Starts a new resilience experiment.

Full OpenAPI interactive documentation is available at `http://localhost:8000/docs`.

## 14. Demo Service Endpoints
The demo service provides standard business endpoints and specific endpoints explicitly designed for injecting failures safely.
- `GET /api/orders`: Returns standard mock data (simulates a database read).
- `GET /api/orders/{order_id}`: Returns a specific mock order.
- `POST /api/experiments/latency`: Injects an artificial delay into all subsequent requests.
  ```json
  { "latency_ms": 500 }
  ```
- `POST /api/experiments/error`: Injects a specific error rate (percentage of requests that will fail with HTTP 500).
  ```json
  { "error_rate": 0.25 }
  ```
- `DELETE /api/experiments`: Instantly resets latency and error rates to zero, restoring normal operation.

## 15. OpenTelemetry Configuration
The demo service utilizes OpenTelemetry auto-instrumentation and programmatic trace generation. The OTEL collector receives these signals via the OTLP protocol (gRPC on port 4317, HTTP on port 4318).
The collector is configured in `observability/otel-collector/otel-collector-config.yaml` to process batches of spans and export them. Metrics are exported to a Prometheus exporter on port 8889, while logs are pushed directly to Loki.

## 16. Prometheus Setup and Useful Queries
Prometheus is configured via `observability/prometheus/prometheus.yml` to scrape both the demo service (`/metrics` on port 8080) and the OTEL collector (`/metrics` on port 8889) every 10 seconds.
Useful PromQL queries you can run in Grafana or the Prometheus UI:
- **Overall Request Rate:** `rate(http_requests_total[5m])`
- **Error Rate (Percentage):** `sum(rate(http_requests_total{status="500"}[5m])) / sum(rate(http_requests_total[5m])) * 100`
- **99th Percentile Latency:** `histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))`
- **Active Go Routines (if using Go backend):** `go_goroutines`

## 17. Grafana Dashboard Access
Access the Grafana UI at `http://localhost:3001`. The default credentials are `admin` / `admin` (you will be prompted to change them on first login, though this can be bypassed in local dev).
Dashboards and Datasources are pre-provisioned. Navigate to the "Dashboards" menu and open the "ResilienceOps" folder. You will find real-time views of service health, request latency distributions, and active experiment indicators.

## 18. SLO and Error Budget Formulas
The backend calculates Service Level Objectives using standard SRE event-based formulas.
- **Availability:** Calculated as `(Eligible Good Events / Eligible Total Events) * 100`.
- **Error Budget:** The maximum allowed failure rate, calculated as `100 - SLO Target Availability`. For a 99.9% target, the error budget is 0.1%.
- **Consumed Budget:** Calculated by tracking the volume of actual bad events against the maximum allowed bad events over the rolling window (e.g., 30 days).
- **Remaining Budget:** `100% - Consumed Budget Percentage`. If this falls below zero, the SLO is breached.

## 19. Alert Evaluation Behavior
The backend alert engine periodically evaluates conditions based on the Prometheus metrics.
Alerts are generated when:
1. Instantaneous error rates exceed defined absolute thresholds (e.g., >5% for 5 minutes).
2. SLO burn rates indicate the error budget will be exhausted before the rolling window ends (e.g., burning budget at 10x the allowed rate for 1 hour).
Alerts can be viewed in the UI and are stored persistently in the database.

## 20. Safe Resilience Experiment Guide
The platform allows operators to perform safe, reversible failure injection to validate observability and alerting.
1. Navigate to the "Experiments" tab in the Frontend dashboard.
2. Select the target service from the dropdown list.
3. Choose the experiment type: "Latency" or "Error".
4. Define the bounds. For safety, latency is hard-capped at 5000ms.
5. Click "Run Experiment". The UI will transition to the active state.
6. Monitor the "Overview" tab and Grafana to observe the telemetry shift. Your alerts should trigger.
7. Click "Stop Experiment" to instantly remove the fault and verify that the system recovers gracefully.

## 21. Kubernetes Manifests
Standard Kubernetes manifests are provided in the `infrastructure/kubernetes/` directory. These include Deployments, Services, and proper security contexts (non-root execution).
To apply them to an existing cluster (e.g., Minikube, kind, or cloud provider):
```bash
kubectl apply -f infrastructure/kubernetes/deployments.yaml
```
Ensure you have provisioned the observability stack (Prometheus/Grafana) in your cluster or update the environment variables to point to external telemetry providers.

## 22. Helm Installation and Upgrade Instructions
A Helm chart is provided for more robust, configurable deployments.
To install the platform using Helm:
```bash
helm install resilienceops ./infrastructure/helm/resilienceops-platform --namespace resilienceops --create-namespace
```
To upgrade an existing installation with new values:
```bash
helm upgrade resilienceops ./infrastructure/helm/resilienceops-platform -f my-custom-values.yaml
```
To uninstall:
```bash
helm uninstall resilienceops -n resilienceops
```

## 23. Terraform Guides (AWS, Azure, GCP)
Terraform examples are located in the `infrastructure/terraform/` directory. They define standard, secure, multi-node Kubernetes clusters using official cloud provider modules.
- **AWS:** Provisions a VPC and an EKS cluster (`infrastructure/terraform/aws`).
- **Azure:** Provisions a Resource Group and an AKS cluster (`infrastructure/terraform/azure`).
- **GCP:** Provisions a GKE cluster with a dedicated node pool (`infrastructure/terraform/gcp`).

**Note:** These are functional examples. Executing `terraform apply` will provision real, paid cloud resources. Ensure you run `terraform destroy` when finished to avoid unexpected charges.

## 24. Testing Commands
To run the automated test suites locally, ensure you have activated your Python virtual environments.
Run all tests using Make (macOS/Linux):
```bash
make test
```
Or run them individually (cross-platform):
```bash
# Backend tests
cd backend
python -m pytest

# Demo Service tests
cd ../demo-service
python -m pytest
```

## 25. CI Workflow
GitHub Actions workflows are defined in `.github/workflows/ci.yml`. They execute automatically on pushes and pull requests to the `main` branch.
The pipeline includes:
- Python dependency installation and `pytest` execution for the backend and demo-service.
- Node.js setup, ESLint static analysis, and a Next.js production build (`npm run build`) for the frontend.
- Terraform formatting and syntax validation (`terraform validate`) for all cloud providers.
- Helm chart linting (`helm lint`).

## 26. Security and Privacy Considerations
- **No Secrets in Code:** Passwords, API keys, and tokens must be supplied via environment variables. None are committed to the repository.
- **Local Isolation:** The resilience experiments are strictly bounded and safe for local development. Do not expose the `/api/experiments` endpoints publicly.
- **Least Privilege:** The Terraform modules are configured to use the minimal necessary IAM roles, and Kubernetes pods are configured to run as non-root users.
- **CORS:** Ensure you configure appropriate Cross-Origin Resource Sharing (CORS) origins in the FastAPI backend if deploying across multiple domains.

## 27. Troubleshooting
- **No Data in Grafana:** Ensure Prometheus is running and the targets are healthy. Visit `http://localhost:9090/targets` to verify the demo-service and otel-collector are up.
- **Services Won't Start (Port Conflicts):** Check if ports 3000, 3001, 8000, 8080, or 9090 are already in use by other local applications. Update `docker-compose.yml` to remap host ports if necessary.
- **Frontend Fails to Connect to API:** Ensure the `NEXT_PUBLIC_API_URL` environment variable matches the exact IP/port where the backend is accessible from your browser (usually `http://localhost:8000/api/v1`).

## 28. Contribution Instructions
We welcome contributions! Please see `CONTRIBUTING.md` for guidelines on submitting pull requests, adhering to coding standards, and running local builds.
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes and ensure tests pass.
4. Open a Pull Request against the `main` branch.

## 29. Roadmap
The project is under active development. Upcoming features include:
- Implementing SSO (OAuth2/OIDC) and Role-Based Access Control (RBAC).
- Adding Tempo or Jaeger for distributed trace visualization within Grafana.
- Expanding resilience experiments to include CPU stress and memory pressure tests.
- Building a Slack/Discord integration for alert notifications.

## 30. Limitations and Project Disclaimer
This platform is an open-source educational implementation designed to demonstrate real Site Reliability Engineering (SRE) and Platform Engineering concepts.
**Do not deploy the failure-injection capabilities to production networks** without implementing robust authentication, authorization, and network isolation. The maintainers assume no liability for outages caused by misusing the experiment API.

## 31. License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
