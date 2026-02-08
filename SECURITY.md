# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability
If you discover a security vulnerability within this project, please open an issue in the tracker (or email the maintainers if provided).

## Local Development Risks
**WARNING:** This project contains endpoints designed to explicitly introduce latency and failure (`/api/experiments`). These are intended **only** for local, bounded resilience testing. 
Do not deploy these endpoints to production or expose them to public networks without implementing strict authentication and authorization controls.
