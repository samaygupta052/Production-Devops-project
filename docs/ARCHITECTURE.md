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
