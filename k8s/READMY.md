# Kubernetes Lab 9 — Application Deployment Documentation

## 1. Architecture Overview

- **Cluster:** Minikube (single-node, local)
- **Application:** Docker image `spalkkina/devops-info-service:1.0`
- **Deployment:** 3 Pod Replicas, managed via Deployment
- **Service:** NodePort exposing the app on port 30080 for external access
- **Pod Resource Allocation:** Requests 128Mi/100m, Limits 256Mi/400m (per pod)
- **Health Checks:** Liveness and readiness probes on `/health`
- **Networking Flow:**

  ```
  [User PC/Browser]
        |
        v
  [NodePort Service (30080)]
        |
        v
  [Pods: devops-info-app (5000)]
  ```

- **Scaling:** Demonstrated up to 5 replicas and rolling update without downtime


## 2. Manifest Files

### 2.1 `deployment.yml`
- **Purpose:** Deploys the app, manages scaling/updates.
- **Key Details:**
  - `replicas: 3` (later scaled to 5)
  - `image: spalkkina/devops-info-service:1.0` (or :latest)
  - `ports: containerPort: 5000`
  - **Resources:** requests/limits as above
  - **Probes:** Both liveness and readiness on `/health` (HTTP GET 5000)
  - **Strategy:** RollingUpdate (`maxUnavailable: 0`, `maxSurge: 1`)
  - **SecurityContext:** Runs as non-root, no privilege escalation

### 2.2 `service.yml`
- **Purpose:** Exposes Pods via NodePort, allowing local access.
- **Key Details:**
  - `type: NodePort`
  - `port: 80`, `targetPort: 5000`, `nodePort: 30080`
  - Selector on `app: devops-info`

## 3. Deployment Evidence

![alt text](<Screenshot 2026-03-26 135120.png>)
![alt text](<Screenshot 2026-03-26 142416.png>)
![alt text](<Screenshot 2026-03-26 142507.png>)
![alt text](<Screenshot 2026-03-26 142729.png>)
![alt text](<Screenshot 2026-03-26 145522.png>)
![alt text](<Screenshot 2026-03-26 142819.png>)
![alt text](<Screenshot 2026-03-26 142836.png>)


## 4. Operations Performed

**Deployment**
```bash
kubectl apply -f k8s/deployment.yml
kubectl apply -f k8s/service.yml
```
**Scaling**
```bash
kubectl scale deployment/devops-info-app --replicas=5
```
![alt text](<Screenshot 2026-03-26 145616.png>)
**Rolling Update**
```bash
# Edit deployment.yml (change image: tag), then:
kubectl apply -f k8s/deployment.yml
kubectl rollout status deployment/devops-info-app
```
  ![alt text](<Screenshot 2026-03-26 145738.png>)
**Rollback**
```bash
kubectl rollout undo deployment/devops-info-app
kubectl rollout history deployment/devops-info-app
```
![alt text](<Screenshot 2026-03-26 145931.png>)
![alt text](<Screenshot 2026-03-26 150020.png>)
**Access and check:**
```bash
minikube ip
curl http://<minikube-ip>:30080/health
```

## 5. Production Considerations

- **Health checks:**  
  Implemented liveness and readiness probes on `/health` for robust failover and traffic management.
- **Resource limits:**  
  Prevents any single Pod from exhausting node resources and enables intelligent scheduling.
- **Rolling update strategy:**  
  Ensures zero-downtime deploys.
- **Run as Non-Root:**  
  SecurityContext to minimize attack surface.
- **Further improvements:**  
  - Use ConfigMap/Secret for configuration/env
  - Add HorizontalPodAutoscaler for real auto-scaling
  - Integrate observability (Prometheus/Grafana) for metrics + logging
  - Store rollout annotations (change-cause)

