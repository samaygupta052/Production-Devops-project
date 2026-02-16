# System Architecture

## High-Level Overview

User → Load Balancer → Kubernetes Ingress → Service → Pods

Pods:
- FastAPI backend container
- React frontend container

Infrastructure:
- AWS EC2 / EKS
- Terraform-managed resources
- Docker images stored in registry

CI/CD Flow:
Developer Push → Jenkins Pipeline →
Build → Scan → Push Image →
Terraform Apply → K8s Deploy →
Smoke Test → Blue/Green Switch

---

## Key Design Principles

- Immutable infrastructure
- Containerized workloads
- Branch-based development
- Fail-fast pipelines
- Observability first
- Rollback always possible

Docker Base Image Decision (Backend)
Current Backend Image Size

The backend Docker image size is approximately 140MB.

This is expected because we are using:
python:3.11-slim

The image includes:
Python runtime
Debian slim OS layer
pip
FastAPI + Uvicorn dependencies
Application source code

Why Not Use Alpine?
An alternative base image is:
python:3.11-alpine

Alpine would reduce image size to approximately 60–70MB.
However, we intentionally chose slim over alpine for production realism.

Technical Difference: slim vs alpine
python:3.11-slim
Based on Debian
Uses glibc
High compatibility with Python packages

Easier debugging
Common in enterprise production systems
python:3.11-alpine

Based on Alpine Linux
Uses musl libc
Smaller image size
Lower compatibility with native Python extensions
May require manual build dependencies
Production Considerations
Alpine can cause issues when using:
psycopg2 (PostgreSQL driver)
cryptography
bcrypt
numpy / pandas
Other C-compiled packages
Because Alpine uses musl instead of glibc, some libraries:
Behave differently
Fail to build
Require additional system dependencies
In enterprise production environments, stability and compatibility are prioritized over small image size.

Decision Rationale
We selected:
python:3.11-slim

Because:
Predictable behavior
Fewer runtime surprises
Better compatibility
Closer to real enterprise production setups
Easier debugging during incidents
The additional ~60MB overhead is acceptable in exchange for stability.

Production Lesson
Smaller image size does not automatically mean better production design.

Trade-offs must consider:
Dependency complexity
Security updates
Debugging ease
Long-term maintainability
Team familiarity
Production engineering prioritizes reliability over optimization unless scaling constraints demand otherwise.
