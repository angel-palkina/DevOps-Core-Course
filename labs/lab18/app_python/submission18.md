# Lab 18 — Reproducible Builds with Nix  


## 1) Nix Installation & Verification

I installed Determinate Nix and verified the version in WSL.

**Result:**  
- `nix (Determinate Nix 3.20.0) 2.34.6`

![alt text](<Screenshot 2026-05-11 124356.png>)_  

---

## 2) Task 1 — Reproducible Build of Python App (Lab 1 Revisit)

### 2.1 Nix Derivation (default.nix)

I created a Nix derivation using `python3Packages.buildPythonApplication` with `makeWrapper` and declared dependencies (`flask`, `prometheus-client`). The derivation builds a runnable `devops-info-service` binary in the Nix store.


---

### 2.2 Reproducibility Proof (Nix Store Path)

I built the app, recorded the store path, rebuilt again, and forced a full rebuild by deleting the store path. The path stayed identical because the hash is computed from the full dependency closure and build instructions.

**Nix store path (both builds):**  
`/nix/store/slimsa8jadicyv44r3v5an3g6zhsf4p0-devops-info-service-1.0.0`

![alt text](<Screenshot 2026-05-11 130604.png>)
![alt text](<Screenshot 2026-05-11 130604-1.png>)
![alt text](<Screenshot 2026-05-11 131859.png>)

---

### 2.3 Reproducibility Hash

I hashed the build output to prove that the result is deterministic.

**Nix output hash:**  
`9717b005b17dd70d5556969f676fa1d50a1654017a06a694687e4eea2af06bb5`

![alt text](<Screenshot 2026-05-11 131926.png>)

---

### 2.4 Comparison with `pip` (Non‑reproducibility)

To demonstrate why `pip` is weaker, I installed `flask` twice without version pinning and compared results. In this run, the versions matched, but this is not guaranteed over time because transitive dependencies are not pinned.

**Diff result:** *(empty — no differences today)*  
```
(diff produced no output)
```

![alt text](<Screenshot 2026-05-11 133547.png>)

**Explanation:**  
- `requirements.txt` only pins direct dependencies.  
- Transitive dependencies can drift.  
- The environment is still time‑dependent.  
- Nix pins the entire dependency graph.

---

### 2.5 Reflection: Why Nix Is More Reproducible than Lab 1 Workflow

- **Lab 1 (`pip`)**: Reproducibility depends on external servers, cache state, and time. Even with version pins, indirect dependencies can change.  
- **Nix**: The exact dependency tree and build inputs are hashed into the store path. Same inputs → same output → bit‑for‑bit identical.

---

## 3) Task 2 — Reproducible Docker Images (Lab 2 Revisit)

### 3.1 docker.nix (Nix dockerTools Image)

I created a Nix Docker image from the same Nix build result, with a **fixed `created` timestamp** for deterministic tarballs.

![alt text](<Screenshot 2026-05-11 134023.png>)
---

### 3.2 Nix Docker Image Reproducibility

I built the image twice and compared SHA256.

**SHA256 (build 1):**  
`b58397dc3fa5d8ecb57d22244c92626b7dfa607292ec57c9136929a581293758`

**SHA256 (build 2):**  
`b58397dc3fa5d8ecb57d22244c92626b7dfa607292ec57c9136929a581293758`  
✅ Identical

![alt text](<Screenshot 2026-05-11 134543.png>)


---

### 3.3 Traditional Dockerfile (Lab 2) Non‑Reproducibility

I rebuilt the Dockerfile **without cache** and compared created timestamps.

**Created timestamps:**  
- `lab2-app:v1` → `2026-05-11T11:01:53.868397927Z`  
- `lab2-app:v2` → `2026-05-11T11:02:28.327824467Z`

**Screenshot 13:** _Both `docker inspect ... | grep Created`_

I also compared `docker save` hashes:

**Hashes:**  
- `lab2-app:v1` → `c5e44008f2afe13bc950463c4589b1546b3e7bc217c4352c59d1fed3505aa452`  
- `lab2-app:v2` → `41138f913703d56e59ab04fe99bb9a45e171ff791f06f85456921ddce7cabeb4`  

✅ Different → Not reproducible

![alt text](<Screenshot 2026-05-11 140438.png>)
![alt text](<Screenshot 2026-05-11 140523.png>)

---

### 3.4 Running Containers Side‑by‑Side

I ran both images with `VISITS_FILE=/tmp/visits` to avoid `/data` permission issues.  

**Health checks:**
- `http://localhost:5000/health`  
  `{"status":"healthy","timestamp":"2026-05-11T11:24:07.364952+00:00","uptime_seconds":20}`

- `http://localhost:5001/health`  
  `{"status":"healthy","timestamp":"2026-05-11T11:24:07.372451+00:00","uptime_seconds":19}`

![alt text](<Screenshot 2026-05-11 142426.png>)

---

## 4) Comparison Summary (Lab 1 vs Lab 18, Lab 2 vs Lab 18)

### Lab 1 (pip) vs Lab 18 (Nix)

| Aspect | Lab 1 (pip/venv) | Lab 18 (Nix) |
|---|---|---|
| Dependency pinning | Direct only | Full transitive closure |
| Reproducibility | Time‑dependent | Bit‑for‑bit |
| Environment isolation | venv | sandboxed build |
| Output identity | Not guaranteed | Deterministic hash |

### Lab 2 Dockerfile vs Nix dockerTools

| Aspect | Dockerfile | Nix dockerTools |
|---|---|---|
| Build timestamps | Change each build | Fixed/deterministic |
| Image hash | Different each build | Identical each build |
| Base image drift | Possible | None (Nix closure) |
| Reproducibility | ❌ | ✅ |

---

## 5) Issues & Fixes

### Problem 1 — Nix image failed to run
Cause: `app.py` had CRLF line endings and no shebang.  
Fix: `dos2unix app.py` + added `#!/usr/bin/env python3`, rebuilt the Nix derivation.

### Problem 2 — Docker container failed to write `/data`
Cause: non‑root user has no write access to `/data`.  
Fix: ran containers with `VISITS_FILE=/tmp/visits`.

---

