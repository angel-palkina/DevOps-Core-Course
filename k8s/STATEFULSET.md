# StatefulSet & Persistent Storage (Lab 15)

This document describes the implementation of **StatefulSet** for the devops‑info application, including headless service, per‑pod PVCs, DNS identity, and persistence verification.

---

## 1) StatefulSet Overview

**Why StatefulSet?**  
StatefulSets provide:
- Stable pod identities (ordered names: `pod-0`, `pod-1`, `pod-2`)
- Stable storage per pod (one PVC per replica)
- Ordered deployment and scaling

**Deployment vs StatefulSet (summary):**

| Feature | Deployment | StatefulSet |
|---------|------------|-------------|
| Pod names | Random suffix | Ordered (pod-0, pod-1) |
| Storage | Shared PVC | Per‑pod PVC via templates |
| Network ID | Dynamic | Stable DNS |
| Scaling | Any order | Ordered |

---

## 2) Resources Verification

After applying Helm chart:

```bash
kubectl get statefulset
kubectl get pods
kubectl get pvc
kubectl get svc
```

![alt text](<Screenshot 2026-05-02 221918.png>)

---

## 3) Headless Service & DNS Identity

Headless service created:
```
devops-info-dev-devops-info-headless (clusterIP: None)
```

DNS resolution from inside the cluster:

```bash
kubectl run -it --rm dnsutils --image=busybox:1.35 --restart=Never -- sh
nslookup devops-info-dev-devops-info-1.devops-info-dev-devops-info-headless.default.svc.cluster.local
```

![alt text](<Screenshot 2026-05-02 222828.png>)

---

## 4) Per‑Pod Storage Isolation

Each pod has its own storage and counter.

Access two pods directly:

```bash
kubectl port-forward pod/devops-info-dev-devops-info-0 8080:5000
kubectl port-forward pod/devops-info-dev-devops-info-1 8081:5000
```

Check counters:
```bash
curl http://localhost:8080/visits
curl http://localhost:8081/visits
```

![alt text](<Screenshot 2026-05-02 223235.png>)
![alt text](<Screenshot 2026-05-02 223402.png>)

---

## 5) Persistence Test

Read value from pod‑0, delete pod, then verify it stays:

```bash
kubectl exec devops-info-dev-devops-info-0 -- cat /data/visits
kubectl delete pod devops-info-dev-devops-info-0
# wait for restart
kubectl exec devops-info-dev-devops-info-0 -- cat /data/visits
```

![alt text](<Screenshot 2026-05-02 223729.png>)
