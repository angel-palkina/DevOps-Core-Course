# ConfigMaps & Persistent Volumes — Lab 12


## 1. Application Changes

### 1.1 Visits counter implementation

The Flask app was updated to store a visits counter in a file:

- data file path: `/data/visits` (configurable via `VISITS_FILE`)
- on startup: initialize file with `0` if missing
- on each `GET /`: increment counter and persist it
- new endpoint `GET /visits`: return current count without incrementing

### 1.2 Concurrency and file safety

Implementation includes:

- `threading.Lock()` for thread-safe increments
- atomic write pattern (`write temp file` + `os.replace`) to reduce file corruption risk

### 1.3 Local Docker testing

A `docker-compose.yml` was created in repository root and mounts host directory to `/data`:

```yaml
volumes:
  - ./data:/data
```

![alt text](<Screenshot 2026-04-15 222158.png>)
![alt text](<Screenshot 2026-04-15 222209.png>)
![alt text](<Screenshot 2026-04-15 222218.png>)

## 2. ConfigMap Implementation

## 2.1 File-based ConfigMap

A chart file was added:

- `k8s/devops-info/files/config.json`

It is loaded into ConfigMap using Helm `.Files.Get` in:

- `k8s/devops-info/templates/configmap.yaml`

Template pattern:

```yaml
data:
  config.json: |-
{{ .Files.Get "files/config.json" | indent 4 }}
```

## 2.2 Environment-variable ConfigMap

A second ConfigMap in the same template provides key-value pairs:

- `APP_ENV`
- `LOG_LEVEL`
- `APP_NAME`

These values come from `values.yaml` (e.g. `environment`, `logLevel`, `appName`).

## 2.3 Deployment wiring

`deployment.yaml` was updated to:

1. Mount file ConfigMap as a volume at `/config`
2. Inject env vars via `envFrom -> configMapRef`

### Mounted file

```yaml
volumeMounts:
  - name: app-config
    mountPath: /config
    readOnly: true
```

```yaml
volumes:
  - name: app-config
    configMap:
      name: {{ include "devops-info.fullname" . }}-config
```

### Env vars

```yaml
envFrom:
  - configMapRef:
      name: {{ include "devops-info.fullname" . }}-env
```

(Combined with existing `secretRef` where needed.)

## 2.4 Verification output

```bash
kubectl exec -it devops-info-dev-devops-info-7d6bb5f6f7-bkjj4 -- cat /config/config.json
kubectl exec -it devops-info-dev-devops-info-7d6bb5f6f7-bkjj4 -- printenv | findstr APP_
```
![alt text](<Screenshot 2026-04-15 224814.png>)



## 3. Persistent Volume Implementation

## 3.1 PVC template

Added file:

- `k8s/devops-info/templates/pvc.yaml`

Configuration:

- access mode: `ReadWriteOnce`
- requested size: `100Mi` (from values)
- optional storage class from values

Values example:

```yaml
persistence:
  enabled: true
  size: 100Mi
  storageClass: ""
```

## 3.2 Deployment volume mount

The application container mounts PVC to `/data`:

```yaml
volumeMounts:
  - name: data-volume
    mountPath: /data
```

And deployment references claim:

```yaml
volumes:
  - name: data-volume
    persistentVolumeClaim:
      claimName: {{ include "devops-info.fullname" . }}-data
```

This stores `/data/visits` on persistent storage, not ephemeral container filesystem.

## 3.3 Persistence test procedure

1. Deploy/upgrade chart
2. Call `/` multiple times to increment counter
3. Check count via `/visits`
4. Delete one pod (`kubectl delete pod <pod-name>`)
5. Wait for replacement pod
6. Re-check `/visits`

![alt text](<Screenshot 2026-04-15 225552.png>)
![alt text](<Screenshot 2026-04-15 225910.png>)
![alt text](<Screenshot 2026-04-15 225721.png>)

## 3.4 Verification commands

```bash
kubectl get configmap,pvc
kubectl get pods
kubectl describe pvc <pvc-name>
kubectl exec -it <pod-name> -- cat /data/visits
```

---

## 4. ConfigMap vs Secret

## ConfigMap

Use for **non-sensitive** configuration:

- feature flags
- app mode/environment
- logging settings
- static config files

## Secret

Use for **sensitive** data:

- passwords
- API keys
- tokens
- certificates/private keys

## Key differences

- ConfigMap data is plain text in Kubernetes API objects.
- Secret data is base64-encoded (and should be protected with RBAC and etcd encryption at rest).
- Operationally, Secrets are intended for confidential data; ConfigMaps are not.
