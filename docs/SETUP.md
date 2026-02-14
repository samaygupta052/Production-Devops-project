# Initial Setup Guide

## Prerequisites

- Linux (Ubuntu recommended)
- Git
- Docker (later phase)
- NodeJS
- Python 3.10+
- AWS CLI (later phase)
- Terraform (later phase)

---

## Repository Setup

git clone <repo>
git checkout develop
git checkout -b devops/initial-setup

---

## Folder Structure Explanation

frontend/     → React application
backend/      → FastAPI application
infra/        → Terraform & Kubernetes
ci-cd/        → Jenkins pipeline configs
scripts/      → Automation scripts
docs/         → Documentation & debugging logs

---

## Branch Policy

- main → production-like
- develop → integration
- feature/* → features
- devops/* → infra & CI/CD
- incident/* → outage simulations
- bugfix/* → fixes
