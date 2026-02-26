# Resilience Experiments Guide

## Principles
1. **Safety First**: Experiments must be bounded (e.g., maximum latency of 5000ms).
2. **Reversibility**: Operators must be able to cancel an experiment at any time, instantly removing the injected fault.
3. **Observability**: An experiment should be clearly visible in telemetry (Grafana) to validate monitoring and alerting rules.

## Available Experiments
- **Latency Injection**: Adds a configurable delay (up to 5 seconds) to specific endpoints in the Demo Service.
- **Error Injection**: Causes a specific percentage of requests to fail with HTTP 500 Internal Server Error.

## Running an Experiment
1. Go to the "Experiments" tab in the Frontend dashboard.
2. Select the target service.
3. Choose the experiment type and configure parameters.
4. Click "Run Experiment".
5. Monitor the "Overview" tab and Grafana to observe the impact.
6. Click "Stop" to conclude the experiment.
