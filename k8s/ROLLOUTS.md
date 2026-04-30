# Argo Rollouts — Progressive Delivery (Lab 14)

## 1) Argo Rollouts Setup

### Controller Installation
```bash
kubectl create namespace argo-rollouts
```

Verification:
```bash
kubectl get pods -n argo-rollouts
```

**Output:**
![alt text](<Screenshot 2026-04-30 210520.png>)

### Dashboard Installation & Access
```bash
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/dashboard-install.yaml
kubectl port-forward svc/argo-rollouts-dashboard -n argo-rollouts 3100:3100
```

Open: `http://localhost:3100`

![alt text](<Screenshot 2026-04-30 210637.png>)

### Rollout vs Deployment (Key Differences)
- **Rollout** supports **canary/blue‑green**, analysis steps, and traffic shifting.
- **Deployment** only supports rolling updates without progressive traffic control.
- Rollout adds `strategy.canary` / `strategy.blueGreen` fields.

---

## 2) Canary Deployment

### Strategy Configuration (Helm)
```yaml
strategy:
  canary:
    steps:
      - setWeight: 20
      - pause: {}
      - setWeight: 40
      - pause: { duration: 30s }
      - setWeight: 60
      - pause: { duration: 30s }
      - setWeight: 80
      - pause: { duration: 30s }
      - setWeight: 100
```

### Deploy Rollout
```bash
helm upgrade --install devops-info-dev . -f values-dev.yaml
```
![alt text](<Screenshot 2026-04-30 215308.png>)

### Watch Canary Progress
```bash
kubectl argo rollouts get rollout devops-info-dev-devops-info -w
```
![alt text](<Screenshot 2026-04-30 215410.png>)


### Manual Promotion
```bash
kubectl argo rollouts promote devops-info-dev-devops-info
```


### Abort / Rollback
```bash
kubectl argo rollouts abort devops-info-dev-devops-info
```

![alt text](<Screenshot 2026-04-30 215410-1.png>)

![alt text](<Screenshot 2026-04-30 215410-2.png>)
---

## 3) Blue‑Green Deployment

### Strategy Configuration (Helm)
```yaml
strategy:
  blueGreen:
    activeService: devops-info-dev-devops-info-service
    previewService: devops-info-dev-devops-info-preview
    autoPromotionEnabled: false
```

### Preview Service (Helm)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: devops-info-dev-devops-info-preview
spec:
  selector:
    app: devops-info
  ports:
    - port: 80
      targetPort: 5000
```

### Deploy Blue‑Green Rollout
```bash
helm upgrade --install devops-info-dev . -f values-dev.yaml -f values-bluegreen.yaml
```
![alt text](<Screenshot 2026-04-30 224127.png>)

### Access Active & Preview

Active:
```bash
kubectl port-forward svc/devops-info-dev-devops-info-service 8080:80
```
Preview:
```bash
kubectl port-forward svc/devops-info-dev-devops-info-preview 8081:80
```

![alt text](<Screenshot 2026-04-30 224211.png>)
![alt text](<Screenshot 2026-04-30 224327.png>)
![alt text](<Screenshot 2026-04-30 224359.png>)
![alt text](<Screenshot 2026-04-30 224504.png>)

### Promote Preview → Active
```bash
kubectl argo rollouts promote devops-info-dev-devops-info
```

### Instant Rollback
```bash
kubectl argo rollouts undo devops-info-dev-devops-info
```

![alt text](<Screenshot 2026-04-30 224814.png>)
![alt text](<Screenshot 2026-04-30 224844.png>)
![alt text](<Screenshot 2026-04-30 224922.png>)
![alt text](<Screenshot 2026-04-30 224934.png>)

---

## 4) Strategy Comparison

| Strategy | Pros | Cons | Best Use Cases |
|----------|------|------|----------------|
| Canary | Gradual traffic shift, safer, lower resource usage | Slower rollout, more complex | Large user base, risk‑sensitive releases |
| Blue‑Green | Instant switch, easy rollback | Requires double resources | Small apps, quick validation, strict rollback needs |

**Recommendation:**  
- Use **Canary** for production services with high traffic and risk.
- Use **Blue‑Green** when fast rollback and simple validation is more important.

---

## 5) CLI Commands Reference

```bash
# Get rollout status
kubectl argo rollouts get rollout devops-info-dev-devops-info -w

# Promote rollout (next step or blue-green)
kubectl argo rollouts promote devops-info-dev-devops-info

# Abort rollout
kubectl argo rollouts abort devops-info-dev-devops-info

# Retry rollout
kubectl argo rollouts retry devops-info-dev-devops-info

# Rollback to previous revision
kubectl argo rollouts undo devops-info-dev-devops-info
```

---
