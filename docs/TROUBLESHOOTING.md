### ❌ Accidental Direct Push to Main Branch
Tool: Git

**What I Was Trying To Do:**
Push initial setup changes to devops/initial-setup branch for review.

**Error / Symptom:**
Accidentally committed and pushed changes directly to the main branch.

Command used:
git push origin main

This violated the branch protection and production workflow policy.

**Root Cause:**
- I was on the wrong branch (main instead of devops/initial-setup).
- Did not verify current branch using `git branch` before pushing.
- No branch protection rules were configured on remote repository.

**How I Debugged:**
1. Checked current branch:
   git branch

2. Checked commit history:
   git log --oneline --graph --decorate

3. Verified what commit was pushed to main:
   git show <commit-id>

4. Checked remote tracking:
   git branch -vv

**Final Fix:**
Used git revert to safely undo the commit without rewriting history:

   git checkout main
   git revert <commit-id>

Then:
- Switched to correct branch:
   git checkout devops/initial-setup
- Re-applied changes properly
- Created Pull Request for review

**Production Lesson:**
- Never push directly to main.
- Always verify branch before committing.
- Enable branch protection rules in remote repository.
- In shared environments, use `git revert` instead of `git reset --hard` to avoid rewriting history.
- Production safety > convenience.

❌ Frontend Worked Without Docker Network
Tool: Docker

What I Was Trying To Do:
Run frontend and backend containers separately without creating a custom Docker network.

Error / Symptom:
There was no visible error. The application worked even though both containers were not attached to a user-defined Docker network.

Root Cause:
The frontend was calling the backend through the host machine using port mapping (-p).
Docker published container ports to the host, allowing browser → host → container communication.

This was not true container-to-container communication.

How I Debugged:
Checked running containers using docker ps
Observed port mappings (8000:8000, 3000:80)
Understood that browser was accessing host ports
Realized no internal Docker DNS resolution was being used

Final Fix:
Created a user-defined Docker network:
docker network create devops-network

Ran both containers inside the same network and used container name:
http://backend:8000

Production Lesson:
Port mapping is not service-to-service communication.
In production systems (Docker Compose, Kubernetes), services communicate over internal networks, not through host ports.
Relying on localhost creates fragile architecture and breaks scaling.

🎯 Production Insight
Right now your system works because:
Browser → Host → Container

In Kubernetes it becomes:
Pod → Service → Pod

Completely different model.

❌ Backend Accessible Without Port Mapping (-p)
Tool: Docker Networking

What I Was Trying To Do:
Run backend container inside a user-defined Docker network without exposing port 8000 to the host using -p, and check whether the frontend container could still access it.

Error / Symptom:
There was no error.
Frontend was still able to communicate with backend even though backend container did not publish port 8000 to the host.

However, accessing http://localhost:8000 from the browser failed.

Root Cause:
Docker containers inside the same user-defined network communicate using internal bridge networking.
Docker provides internal DNS resolution.
Containers resolve each other using container names.
Communication happens via internal container IP and exposed container port.
Port publishing (-p) is only required for host-to-container communication.

So:
Frontend → http://backend:8000 → Backend (internal Docker network)

But:
Browser → http://localhost:8000 → ❌ Fails
Because port was not published to host.

How I Debugged:
Commands used:
docker ps
docker inspect backend
docker network inspect devops-network

Observed:
Backend container had no published ports.
Both containers were attached to devops-network.
Frontend successfully resolved backend via Docker DNS.

Tested:
curl http://backend:8000/health inside frontend container → Success
curl http://localhost:8000 on host → Failed

Final Fix:
No fix required. This behavior is correct and production-aligned.
If host access is required:
docker run -p 8000:8000 ...

If only internal service communication is required, no port publishing is needed.

Production Lesson:
Port publishing is for host access, not container communication.

In production systems:
Backend services are typically internal-only.
Only frontend or API gateway is publicly exposed.
Internal service communication happens over private networking (Docker bridge, Kubernetes Service, VPC networking).

Understanding this distinction prevents accidental public exposure of internal services and improves security architecture.

### ❌ Frontend Cannot Reach Backend When Using Docker Compose

Tool: Docker / Docker Compose / Nginx

**What I Was Trying To Do:**

I containerized both FastAPI backend and React frontend.
When running containers separately using `docker run`, the frontend successfully connected to the backend using `http://localhost:8000`.

After switching to Docker Compose and updating the frontend API URL to `http://backend:8000`, the frontend failed to fetch data from the backend.

---

**Error / Symptom:**

Browser console error:

Cross-Origin Request Blocked: The Same Origin Policy disallows reading the remote resource at http://backend:8000/api/message.
Reason: CORS request did not succeed.
Status code: (null)

Frontend showed:
TypeError: NetworkError when attempting to fetch resource

Backend logs showed no incoming API request.

---

**Root Cause:**

The frontend application runs in the user's browser, not inside the Docker container.

`backend` is a Docker internal DNS name that is only resolvable inside the Docker network.

When the browser tried to call:
http://backend:8000

It failed because:

- The browser runs on the host machine
- The host machine cannot resolve Docker internal service names
- The request failed at DNS level
- Therefore status code was null
- Backend never received the request

This is not a CORS configuration problem.
It is a networking scope problem.

---

**How I Debugged:**

1. Checked browser DevTools → Network tab
2. Observed request failing with status (null)
3. Verified backend container logs (no incoming request)
4. Tested curl inside frontend container:
   curl http://backend:8000/health
   → Worked successfully
5. Confirmed that Docker internal DNS resolution works only inside containers
6. Realized browser cannot access Docker service names

---

**Final Fix:**

Implemented Nginx reverse proxy inside frontend container.

Steps:

1. Created `nginx.conf`
2. Configured:

   location /api/ {
       proxy_pass http://backend:8000/api/;
   }

3. Modified frontend Dockerfile to copy custom nginx.conf
4. Changed frontend API call from:
   http://backend:8000/api/message
   to:
   /api/message

Now flow is:

Browser → localhost:3000 → Nginx → backend container

No direct browser-to-backend call.
No cross-origin issue.

---
**Production Lesson:**

- Browser networking and container networking are different layers.
- Docker service names are not accessible from the host machine.
- A CORS error can actually be a DNS/network resolution issue.
- Frontend applications should not directly depend on backend container hostnames.
- Reverse proxy (Nginx) is the correct production architecture.
- In real production systems, API traffic is routed via Load Balancer or reverse proxy, not direct container access.
