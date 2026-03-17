# Lab 07: Logging and Monitoring with Loki and Grafana

**Student:** Sofa Palkina  
**Course:** DevOps  
**Date:** March 2026



## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Docker Host                       │
│                                                     │
│  ┌──────────────┐      ┌──────────────┐           │
│  │  Python App  │      │   Grafana    │           │
│  │  (port 5000) │      │  (port 3000) │           │
│  └──────┬───────┘      └──────┬───────┘           │
│         │ logs                 │ queries            │
│         ▼                      ▼                    │
│  ┌──────────────┐      ┌──────────────┐           │
│  │  Promtail    │─────▶│     Loki     │           │
│  │  (port 9080) │ push │  (port 3100) │           │
│  └──────────────┘      └──────────────┘           │
│         │                                           │
│         └─ Collects logs from:                     │
│            - Docker containers                      │
│            - /var/lib/docker/containers            │
└─────────────────────────────────────────────────────┘
```

### Components

#### 1. Grafana Loki (v3.0.0)
- **Purpose:** Log aggregation and storage
- **Port:** 3100
- **Storage:** Filesystem-based (local volume)
- **Retention:** 168 hours (7 days)
- **Resources:** 1 CPU / 1GB RAM

#### 2. Promtail (v3.0.0)
- **Purpose:** Log collection agent
- **Port:** 9080
- **Method:** Docker service discovery
- **Targets:** All Docker containers
- **Resources:** 0.5 CPU / 512MB RAM

#### 3. Grafana (v11.3.0)
- **Purpose:** Visualization and dashboards
- **Port:** 3000
- **Authentication:** Required (admin/admin)
- **Data source:** Loki
- **Resources:** 1 CPU / 512MB RAM

#### 4. Python Flask App (v2.0)
- **Purpose:** Sample application with structured logging
- **Port:** 5000
- **Logging:** JSON format
- **Endpoints:** `/`, `/health`
- **Resources:** 0.5 CPU / 256MB RAM

##  Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2+
- 4GB RAM available
- Windows 10/11 or Linux

### Create Environment File

Create `.env` file:

```env
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

###  Start Services

```bash
docker compose up -d
```

### Wait for Services

Wait ~30 seconds for all health checks to pass:

```bash
docker compose ps
```

Expected output:
```
NAME            STATUS
loki            Up (healthy)
promtail        Up
grafana         Up (healthy)
devops-python   Up (healthy)
```
![alt text](<Screenshot 2026-03-12 173203.png>)

### Access Grafana

Open browser: http://localhost:3000

Login:
- **Username:** admin
- **Password:** admin

### Query Logs in Grafana

**Basic queries:**

```logql
# All logs from Python app
{container="devops-python"} | json

# Only GET requests
{container="devops-python"} | json | method="GET"

# Only errors (status >= 400)
{container="devops-python"} | json | status >= 400

# Only WARNING/ERROR levels
{container="devops-python"} | json | level!="INFO"

# Logs from specific path
{container="devops-python"} | json | path="/health"
```
![alt text](<Screenshot 2026-03-12 161402.png>)
![alt text](<Screenshot 2026-03-12 161429.png>)
![alt text](<Screenshot 2026-03-12 161346.png>)
![alt text](<Screenshot 2026-03-12 161257.png>)

**Metrics queries:**

```logql
# Request rate (requests per second)
sum(rate({container="devops-python"} | json | __error__="" [1m]))

# Log count by level
sum by (level) (count_over_time({container="devops-python"} | json [5m]))

# Error rate
sum(rate({container="devops-python"} | json | status >= 400 [1m]))
```

### Access Service UIs

- **Grafana:** http://localhost:3000
- **Promtail Targets:** http://localhost:9080/targets
- **Loki Ready:** http://localhost:3100/ready
- **Python App:** http://localhost:5000


## Configuration

### Loki Configuration (`loki/config.yml`)

```yaml
# Key settings:
retention_period: 168h        # 7 days
compactor:
  retention_enabled: true
  delete_request_store: filesystem
```

### Promtail Configuration (`promtail/config.yml`)

```yaml
# Collects logs from all Docker containers
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
```

### Python App Logging

Custom JSON formatter:
```json
{
  "timestamp": "2026-03-12T14:30:00.123Z",
  "level": "INFO",
  "message": "Request completed",
  "method": "GET",
  "path": "/health",
  "status": 200,
  "client_ip": "172.23.0.1"
}
```
## Dashboard

### Panels

1. **Application Logs** (Logs visualization)
   - Shows all application logs in table format
   - Time, level, message, HTTP details

2. **Request Rate** (Time series)
   - Requests per second over time
   - Helps identify traffic patterns

3. **Errors & Warnings** (Logs visualization)
   - Filtered view of errors only
   - Quick error detection

4. **Log Level Distribution** (Stat/Pie chart)
   - Count of logs by level (INFO, WARNING, ERROR)
   - Last 5 minutes
![alt text](<Screenshot 2026-03-12 172002.png>)


## Challenges

### Services Not Starting

```bash
# Check logs
docker compose logs loki
docker compose logs promtail
docker compose logs grafana

# Restart services
docker compose restart
```

### No Logs in Grafana

**Check Promtail targets:**
```bash
curl http://localhost:9080/targets
```

**Check Promtail logs:**
```bash
docker logs promtail --tail 50
```

**Verify Loki is receiving logs:**
```bash
curl http://localhost:3100/loki/api/v1/label/__name__/values
```

### Loki Health Check Failing

**Check configuration:**
```bash
docker exec loki cat /etc/loki/config.yml
```

**Common issue:** Missing `delete_request_store` in compactor config.

**Fix:** Ensure `loki/config.yml` has:
```yaml
compactor:
  delete_request_store: filesystem
```

### Python App Unhealthy

**Check if app is running:**
```bash
curl http://localhost:5000/health
```

**Check health check command:**
```bash
docker exec devops-python python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"
```

## Production Readiness

### Resource Limits

All services have CPU and memory limits:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Health Checks

All critical services have health checks:
- **Loki:** HTTP check on `/ready`
- **Grafana:** HTTP check on `/api/health`
- **Python App:** Python-based HTTP check on `/health`

### Security

✅ Anonymous access disabled  
✅ Strong admin password (configured via `.env`)  
✅ User signup disabled  
✅ Secrets in `.env` file (not in git)  
![alt text](<Screenshot 2026-03-12 173316.png>)

### Monitoring

Check service health:
```bash
docker compose ps
docker stats --no-stream
```

Check resource usage:
```bash
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```
![alt text](<Screenshot 2026-03-12 173234.png>)

