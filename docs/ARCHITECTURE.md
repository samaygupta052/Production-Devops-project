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

# Nginx – Role in Our Architecture

## What Is Nginx?

Nginx (pronounced "engine-x") is a high-performance web server and reverse proxy server.

It is commonly used for:

- Serving static files (HTML, CSS, JS)
- Reverse proxying requests to backend services
- Load balancing
- SSL termination
- API gateway behavior
- Handling high concurrent traffic efficiently

Nginx is event-driven and asynchronous, which makes it extremely efficient under high load.

---

## Why We Use Nginx in This Project

In our Docker Compose setup, we use Nginx inside the frontend container.

It performs two critical responsibilities:

### 1. Static File Server

After building the React app:

npm run build

It generates static files inside the `dist/` folder.

Nginx serves those static files to users when they visit:

http://localhost:3000

Without Nginx, the container would not be able to serve production-ready static assets efficiently.

---

### 2. Reverse Proxy for Backend API

Instead of allowing the browser to directly call:

http://backend:8000/api/message

(which failed due to Docker DNS isolation and browser networking limitations),

We configured Nginx to proxy API requests internally:

Browser → localhost:3000 → Nginx → backend container

This works because:

- Nginx runs inside Docker
- It can resolve Docker service names like `backend`
- The browser does not need to know backend hostname
- No cross-origin request occurs

This eliminates CORS and DNS issues cleanly.

---

## What Is a Reverse Proxy?

A reverse proxy is a server that:

- Receives client requests
- Forwards them to backend services
- Returns backend response to the client

The client never directly communicates with backend services.

In our case:

location /api/ {
    proxy_pass http://backend:8000/api/;
}

When the browser calls:

/api/message

Nginx forwards it internally to:

http://backend:8000/api/message

---

## Why Not Call Backend Directly?

When using Docker Compose:

- `backend` is a Docker internal DNS name
- The browser runs on the host machine
- The host cannot resolve Docker internal DNS names

So calling:

http://backend:8000

from browser fails.

Using Nginx avoids this architectural mistake.

---

## Production Relevance

In real production environments:

Browser → Load Balancer → Reverse Proxy (Nginx) → Application Servers

Direct service-to-service exposure is avoided because:

- It creates security risks
- It complicates CORS
- It tightly couples frontend and backend
- It breaks in distributed environments

Using Nginx gives:

- Clean routing
- Centralized traffic control
- Better scalability
- Security boundary
- Production-ready architecture

---

## Key Lesson Learned

- Docker internal networking is isolated from host networking.
- Browser networking and container networking are separate layers.
- CORS errors can sometimes indicate network resolution problems.
- Reverse proxy architecture is the correct production design.
- Infrastructure design matters more than quick fixes.


