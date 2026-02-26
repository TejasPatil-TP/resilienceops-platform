# Operations Runbook

## Restarting Services
To restart the entire stack:
```bash
make down
make up
```

## Database Migrations
To apply a new migration to the backend database:
```bash
cd backend
alembic upgrade head
```

## Adding a New Dashboard
1. Edit or create a new JSON dashboard in `observability/grafana/dashboards/`.
2. Grafana will automatically pick up the changes via its provisioning configuration within 10 seconds.

## Dealing with Port Conflicts
If you cannot start the stack because of port conflicts, update the `docker-compose.yml` to map host ports to available ones.
Default ports:
- 3000: Frontend
- 8000: Backend
- 8080: Demo Service
- 3001: Grafana
- 9090: Prometheus
