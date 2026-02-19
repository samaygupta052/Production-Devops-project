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

❌ ImagePullBackOff in Minikube
Tool: Kubernetes (Minikube)

What I Was Trying To Do:
Deploy backend and frontend containers to Minikube using locally built Docker images (devops-backend:latest, devops-frontend:latest).

Error / Symptom:
Pods stuck in:

ImagePullBackOff
kubectl get pods -n devops
Output:
backend-xxxxx   0/1   ImagePullBackOff

Root Cause:
Minikube runs its own Docker daemon internally.
The images were built in the host Docker daemon, not inside Minikube’s Docker environment.

Therefore, Kubernetes could not find the images and tried pulling from a registry, which failed.

How I Debugged:
Checked pod status:
kubectl get pods -n devops

Described pod:
kubectl describe pod <pod-name> -n devops

Observed:
Failed to pull image "devops-backend:latest"

Checked minikube Docker environment:
eval $(minikube docker-env)
docker images

Images were missing.

Final Fix:
Switched to Minikube Docker daemon:
eval $(minikube docker-env)

Rebuilt images:
docker build -t devops-backend ./backend
docker build -t devops-frontend ./frontend

Re-applied deployment:
kubectl delete pod <pod-name> -n devops

Pods moved to Running state.

Production Lesson:
Kubernetes nodes must have access to container images.
In production, this means pushing images to a container registry (ECR, Docker Hub, etc.).
Local images are invisible to cluster nodes unless built inside the same runtime environment.

❌ Service Not Routing Traffic (Selector Mismatch)
Tool: Kubernetes

What I Was Trying To Do:
Expose backend using a ClusterIP service and allow frontend to communicate with it.

Error / Symptom:
Pods were running successfully:

kubectl get pods -n devops

But application could not connect to backend.
Service existed but traffic was not routed.

Root Cause:
Service selector did not match pod labels.

Deployment label:
labels:
  app: backend

Service selector mistakenly configured as:
selector:
  app: backend-wrong

Because of this mismatch, the service had no endpoints.

How I Debugged:
Checked services:
kubectl get svc -n devops

Checked endpoints:
kubectl get endpoints -n devops

Observed:
backend   <none>

Which means service is not attached to any pods.

Verified pod labels:
kubectl get pods --show-labels -n devops

Compared with service selector.

Final Fix:
Corrected service selector:
selector:
  app: backend

Re-applied:
kubectl apply -f backend-service.yaml

Checked endpoints again:
kubectl get endpoints -n devops

Now endpoints showed pod IP.
Application started working.

Production Lesson:
In Kubernetes, services route traffic using labels — not names.
A label mismatch causes silent traffic failure even if pods are healthy.
Always verify selectors and endpoints during service-related issues.

🧠 How To Access Application Running in Pod
There are multiple ways depending on service type.

🔹 1️⃣ Access Using NodePort (Frontend Service)

If frontend service type is:
type: NodePort

Find service:
kubectl get svc -n devops

Example output:
frontend   NodePort   10.96.x.x   <none>   80:31245/TCP

Access using Minikube:
minikube service frontend -n devops

OR manually:
http://<minikube-ip>:<nodeport>

Get IP:
minikube ip

🔹 2️⃣ Port Forward (Direct Pod Access)
For debugging backend:
kubectl port-forward pod/<pod-name> 8000:8000 -n devops

Now access locally:
http://localhost:8000/health

This bypasses service completely.
Very useful for debugging.

🔹 3️⃣ Exec Into Pod
kubectl exec -it <pod-name> -n devops -- sh

Then test internally:
curl localhost:8000/health

Useful when debugging internal connectivity.

🔹 4️⃣ Test Service From Inside Cluster

Launch temporary pod:
kubectl run test --rm -it --image=busybox -n devops -- sh

Inside:
wget -qO- http://backend:8000/health

This tests service DNS inside cluster.

🚀 Production Debug Command Summary
Purpose	Command
See pods	kubectl get pods -n devops
Pod details	kubectl describe pod <pod> -n devops
Pod logs	kubectl logs <pod> -n devops
See services	kubectl get svc -n devops
Check endpoints	kubectl get endpoints -n devops
Show labels	kubectl get pods --show-labels -n devops
Port forward	kubectl port-forward pod/<pod> 8000:8000 -n devops
Exec inside pod	kubectl exec -it <pod> -n devops -- sh


❌ CrashLoopBackOff Due to Invalid Container Command
Tool: Kubernetes

What I Was Trying To Do:
Deploy backend container to Kubernetes cluster.
Error / Symptom:
Pod status showed:
CrashLoopBackOff

Root Cause:
Container command overridden in deployment YAML with invalid Python file:
command: ["python", "wrongfile.py"]

Container exited immediately with error code 2.
Kubernetes restarted container repeatedly, resulting in CrashLoopBackOff.

How I Debugged:
Checked pod:
kubectl get pods -n devops

Described pod:
kubectl describe pod <pod-name> -n devops

Checked logs:
kubectl logs <pod-name> -n devops

Checked previous logs:
kubectl logs <pod-name> -n devops --previous

Observed Python file not found error.

Final Fix:
Removed incorrect command override from deployment YAML and reapplied.

Production Lesson:
CrashLoopBackOff usually means application inside container is failing immediately.
Always check container logs before assuming infrastructure issue.


❌ Readiness Probe Failure
Tool: Kubernetes

What I Was Trying To Do:
Ensure backend is ready before receiving traffic.

Error / Symptom:
Pod status:
Running 0/1

Service endpoints empty.

Root Cause:
Readiness probe path incorrect (/wrong-health).
Probe returned 404.

How I Debugged:
kubectl get pods -n devops
kubectl describe pod <pod-name> -n devops
kubectl get endpoints -n devops

Observed readiness probe failed in events.

Final Fix:
Corrected probe path to /health.

Production Lesson:
If readiness fails, traffic stops even if container is running.
This can cause partial outages without obvious crashes.

❌ Liveness Probe Causing Pod Restarts
Tool: Kubernetes

What I Was Trying To Do:
Ensure container restarts if unhealthy.

Error / Symptom:
Pod continuously restarting.
Eventually CrashLoopBackOff.

Root Cause:
Liveness probe path incorrect.
Probe failure caused Kubernetes to kill container repeatedly.

How I Debugged:
kubectl describe pod <pod-name> -n devops
kubectl get pods -n devops -w

Observed repeated liveness probe failures.

Final Fix:
Corrected liveness probe path to /health.

Production Lesson:
Liveness probes can cause cascading failures if misconfigured.
Never configure aggressive probes without testing.


❌ OOMKilled Due to Low Memory Limit
Tool: Kubernetes

What I Was Trying To Do:
Configure memory limits for backend container.

Error / Symptom:
Pod restarted automatically.
kubectl describe pod showed:

Reason: OOMKilled

Root Cause:
Memory limit set to 64Mi.
Application consumed more memory during /memory-spike endpoint call.
Kernel OOM killer terminated container.

How I Debugged:
kubectl get pods -n devops
kubectl describe pod <pod-name> -n devops
kubectl get pods -n devops -w

Observed OOMKilled in Last State.

Final Fix:
Increased memory limit to 256Mi.

Production Lesson:
Setting aggressive memory limits can cause unexpected restarts under load.
Always load-test before setting strict limits.
Requests and limits must reflect real usage patterns.

❌ ConfigMap Not Found (CreateContainerConfigError)
Tool: Kubernetes

What I Was Trying To Do:
Inject environment variables using ConfigMap.

Error / Symptom:
Pod stuck in:
CreateContainerConfigError

Root Cause:
Deployment referenced non-existent ConfigMap.

How I Debugged:
kubectl get pods -n devops
kubectl describe pod <pod-name> -n devops

Observed error in Events section.

Final Fix:
Corrected ConfigMap name and reapplied deployment.

Production Lesson:
Configuration mismatches can prevent pods from starting.
Always verify existence of referenced resources.

❌ Secret Missing (CreateContainerConfigError)
Tool: Kubernetes

What I Was Trying To Do:
Inject sensitive values via Secret.

Error / Symptom:
Pod failed to start with:
secret "backend-secret" not found

Root Cause:
Secret was deleted but still referenced in deployment.

How I Debugged:
kubectl describe pod <pod-name> -n devops

Checked events for missing secret.

Final Fix:
Recreated Secret resource.

Production Lesson:
Secrets are critical dependencies.
Missing secrets can cause full service outage.
Secret management must be handled carefully in CI/CD.


❌ Ingress 502 Bad Gateway (Wrong Service Name)
Tool: Kubernetes Ingress

What I Was Trying To Do:
Route traffic to frontend service using Ingress.

Error / Symptom:
Browser showed:

502 Bad Gateway

Root Cause:
Ingress referenced non-existent service name.

How I Debugged:
kubectl describe ingress devops-ingress -n devops
kubectl get svc -n devops
kubectl logs <ingress-controller-pod> -n ingress-nginx

Observed service not found.

Final Fix:
Corrected service name in ingress.yaml.

Production Lesson:
Ingress errors often appear as 502.
Always verify service name and port mapping.

❌ Ingress Port Mismatch
Tool: Kubernetes Ingress

What I Was Trying To Do:
Expose frontend via Ingress.

Error / Symptom:
502 error despite service existing.

Root Cause:
Ingress pointed to incorrect service port (9999).

How I Debugged:
kubectl describe ingress devops-ingress -n devops
kubectl get svc -n devops

Compared service port with ingress backend port.

Final Fix:
Updated ingress backend port to correct service port (80).

Production Lesson:
Ingress must reference service port — not container port.
Port mismatches are a common routing failure.
