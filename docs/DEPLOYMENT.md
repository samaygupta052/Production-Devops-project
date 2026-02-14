# Deployment Strategy

## CI/CD Pipeline Stages

1. Checkout
2. Lint
3. Unit Test
4. Docker Build
5. SonarQube Scan
6. Trivy Scan
7. Push Image
8. Terraform Plan
9. Terraform Apply
10. Kubernetes Deploy
11. Smoke Test
12. Blue-Green Switch
13. Rollback (if required)

---

## Deployment Strategy

Blue-Green deployment using:

- Two deployments
- Service selector switch
- Traffic rerouting via Ingress
