# Security Review

## Threat Model & Findings

1. **Unauthenticated API Access**
   - **Risk**: The backend API and demo service currently lack authentication.
   - **Mitigation**: This project is designed for local demonstration and educational purposes. If deployed to a real environment, integrate an Identity Provider (IdP) and enforce RBAC.
   
2. **Resilience Experiments Abuse**
   - **Risk**: An attacker could use the `/api/experiments` endpoints to launch a DoS attack by injecting 5000ms latency or 100% error rates.
   - **Mitigation**: Bounds checking is implemented in the application logic (e.g., max 5000ms latency). In a production scenario, these endpoints should be disabled or strictly firewalled.
   
3. **Secret Management**
   - **Risk**: Hardcoded secrets in code.
   - **Mitigation**: The project uses `.env` variables and docker-compose environment blocks. No secrets are committed to the repository.
   
4. **Container Security**
   - **Risk**: Containers running as root.
   - **Mitigation**: Kubernetes manifests explicitly set `runAsNonRoot: true` and `runAsUser: 1000`. Dockerfiles should ideally use non-root users as well.

## Recommendations
- Implement OAuth2/OIDC for the frontend and backend.
- Enforce network policies in Kubernetes to restrict access to the `/api/experiments` endpoints.
