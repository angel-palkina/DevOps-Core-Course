# Lab 16 — Kubernetes Monitoring & Init Containers

## Stack Components

- **Prometheus Operator** — manages Prometheus and Alertmanager as Kubernetes CRDs (simplifies setup and updates).
- **Prometheus** — scrapes metrics from exporters and stores time‑series data.
- **Alertmanager** — handles alerts from Prometheus and groups/routs notifications.
- **Grafana** — visualizes metrics with dashboards and panels.
- **kube-state-metrics** — exposes Kubernetes object state (deployments, pods, nodes, etc.) as metrics.
- **node-exporter** — exports node‑level metrics (CPU, memory, disk, network, load).

---

## Installation Evidence

**Command:**
```bash
kubectl get pods,svc -n monitoring
```
![alt text](<Screenshot 2026-05-09 190529.png>)


---

## Dashboard Answers

### 1) Pod Resources — CPU & Memory usage of StatefulSet
Dashboard: **Kubernetes / Compute Resources / Pod**  
StatefulSet pods show CPU and Memory usage.
![alt text](<Screenshot 2026-05-09 210312.png>)
![alt text](<Screenshot 2026-05-09 210156.png>)
---

### 2) Namespace Analysis — Most/Least CPU in default namespace
Dashboard: -

![alt text](<Screenshot 2026-05-09 191808.png>)
---

### 3) Node Metrics — Memory usage (% and MB), CPU cores
Dashboard: **Node Exporter / Nodes**

- Memory usage gauge shows **~60.9%**
- 16 CPU cores

![alt text](<Screenshot 2026-05-09 191945.png>)

---

### 4) Kubelet — Pods/Containers managed
Dashboard: **Kubernetes / Kubelet**

- Running Pods: **39**
- Running Containers: **84**

![alt text](<Screenshot 2026-05-09 192144.png>)

---

### 5) Network — Traffic for pods in default namespace
The `container_network_*` metrics were not exposed, so I used node‑exporter metrics instead:

- **Receive:** `node_network_receive_bytes_total`
- **Transmit:** `node_network_transmit_bytes_total`

![alt text](<Screenshot 2026-05-09 215714.png>)
![alt text](<Screenshot 2026-05-09 215757.png>)

---

### 6) Alerts — Active alerts count (Alertmanager)
Dashboard: **Alertmanager / Overview**

![alt text](<Screenshot 2026-05-09 192436.png>)
![alt text](<Screenshot 2026-05-09 192540.png>)

---

## Init Containers — Implementation and Proof

### Implementation (StatefulSet)
Init containers were added to `statefulset.yaml`:

- **init-download**: downloads `index.html` into shared volume `/work-dir`
- **wait-for-kubernetes**: waits until `kubernetes.default.svc` is resolvable

---

### Proof of Success

![alt text](<Screenshot 2026-05-09 232953.png>)
![alt text](<Screenshot 2026-05-09 233027.png>)
![alt text](<Screenshot 2026-05-09 233027-1.png>)
![alt text](<Screenshot 2026-05-09 233104.png>)