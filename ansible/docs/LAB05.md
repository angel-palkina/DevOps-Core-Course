# LAB05 — Ansible Fundamentals

**Author:** Sofia Palkina  
**Date:** 2026-02-26  
**Course:** DevOps Core Course  

---

## 1. Architecture Overview

### Ansible Version


**Version:** `ansible [core 2.20.3]`  
**Python:** `3.12.3`  
**Platform:** Ubuntu 24.04 LTS (WSL2)

---

### Target VM Configuration

| Parameter | Value |
|-----------|-------|
| **Cloud Provider** | Yandex Cloud |
| **Provisioning Tool** | Terraform |
| **OS** | Ubuntu 22.04 LTS |
| **Public IP** | `89.169.158.252` |
| **Internal IP** | `192.168.10.30` |
| **SSH User** | `ubuntu` |
| **Connection** | SSH with key authentication |

---

### Role Structure

```
ansible/
├── ansible.cfg                   # Ansible configuration
├── inventory/
│   ├── hosts.ini                 # Static inventory
│   └── group_vars/
│       └── all.yml              # Encrypted variables (Vault)
├── roles/
│   ├── common/                   # System provisioning
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   └── defaults/
│   │       └── main.yml
│   ├── docker/                   # Docker installation
│   │   ├── tasks/
│   │   │   └── main.yml
│   │   ├── handlers/
│   │   │   └── main.yml
│   │   └── defaults/
│   │       └── main.yml
│   └── app_deploy/               # Application deployment
│       ├── tasks/
│       │   └── main.yml
│       ├── handlers/
│       │   └── main.yml
│       └── defaults/
│           └── main.yml
├── playbooks/
│   ├── provision.yml             # System provisioning playbook
│   └── deploy.yml                # Application deployment playbook
└── docs/
    ├── LAB05.md                  # This documentation
    └── screenshots_l5/           # Screenshots
```

---

### Why Roles Instead of Monolithic Playbooks?

**Roles provide:**

1. **Modularity** — Each role has a single responsibility
   - `common`: System packages
   - `docker`: Docker installation
   - `app_deploy`: Application deployment

2. **Reusability** — Roles can be shared across projects
   - Docker role works on any Ubuntu server
   - No code duplication

3. **Maintainability** — Changes isolated to specific roles
   - Update Docker version in one place
   - Clear separation of concerns

4. **Testability** — Test roles independently
   - Verify Docker installation separately
   - Gradual deployment
---

## 2. Roles Documentation

### Role: `common`

#### Purpose

Performs basic system provisioning for Ubuntu servers:
- Updates apt package cache
- Installs essential system packages
- Configures timezone (optional)

This role prepares any Ubuntu server for further automation by ensuring common tools are available.

#### Tasks Implementation

**File:** `roles/common/tasks/main.yml`


#### Variables

**File:** `roles/common/defaults/main.yml`


**Variable Explanation:**
- `common_packages`: List of essential packages
- Can be overridden in inventory or playbook

#### Handlers

None required — package installation doesn't need service restarts.

#### Dependencies

None — this is typically the first role executed.

#### Idempotency

-  `apt: state=present` — installs only if missing
-  `update_cache` with `cache_valid_time` — caches for 1 hour
-  Multiple runs don't change system if packages exist

---

### Role: `docker`

#### Purpose

Installs and configures Docker Engine on Ubuntu:
1. Adds Docker official GPG key
2. Adds Docker APT repository
3. Installs Docker CE packages
4. Configures Docker service (enable, start)
5. Adds user to `docker` group
6. Installs Python Docker SDK for Ansible modules

#### Tasks Implementation

**File:** `roles/docker/tasks/main.yml`

#### Variables

**File:** `roles/docker/defaults/main.yml`

**Variable Explanation:**
- `docker_user`: User to add to docker group (enables non-root Docker commands)

#### Handlers

**File:** `roles/docker/handlers/main.yml`

**Handler Explanation:**
- Triggered when Docker repository is added
- Ensures Docker service uses new configuration
- Only runs when needed (efficiency!)

#### Dependencies

Should run after `common` role (requires `curl`, `apt-transport-https`).

#### Idempotency

- `apt_key: state=present` — adds key only if missing
- `apt_repository: state=present` — adds repo only if missing
- `service: state=started` — starts only if stopped
-  `user: append=yes` — adds to group without removing other groups

---

### Role: `app_deploy`

#### Purpose

Deploys containerized Python application from Docker Hub:
1. Authenticates with Docker Hub (using Vault credentials)
2. Pulls latest Docker image
3. Stops and removes old container (if exists)
4. Runs new container with proper configuration
5. Verifies deployment health

#### Tasks Implementation

**File:** `roles/app_deploy/tasks/main.yml`

#### Variables

**Encrypted Variables** (from Vault):

**File:** `inventory/group_vars/all.yml` (encrypted)

```yaml
---
# Docker Hub credentials
dockerhub_username: spalkkina
dockerhub_password: <encrypted-token>

# Application configuration
app_name: devops-info-service
docker_image: "{{ dockerhub_username }}/{{ app_name }}"
docker_image_tag: "1.0"
app_port: 5000
app_port_2: 6000
app_container_name: "{{ app_name }}"
```

**Default Variables:**

**File:** `roles/app_deploy/defaults/main.yml`

**Variable Explanation:**
- `dockerhub_username/password`: Docker Hub authentication (from Vault)
- `docker_image`: Full image name 
- `docker_image_tag`: Image version to deploy
- `app_port`: Host port (external)
- `app_port_2`: Container port 
- `docker_restart_policy`: `unless-stopped` (auto-restart on reboot)
- `app_environment_vars`: Custom environment variables (empty by default)

#### Handlers

**File:** `roles/app_deploy/handlers/main.yml`

**Handler Explanation:**
- Restarts container when configuration changes
- Used for config updates without redeployment

#### Dependencies

**Requires:**
- `docker` role executed first
- Docker daemon running
- Python Docker SDK installed

#### Security Considerations

- `no_log: true` on Docker login (prevents credentials in logs)
- Credentials stored in Ansible Vault
- Vault password not committed to repository

#### Idempotency

- `docker_container: state=started` — starts only if not running
- Image pull only downloads if newer version exists
- Container recreated only if config changes

---

## 3. Idempotency Demonstration

### Concept

**Idempotency:** Running the same operation multiple times produces the same result.

In Ansible: Re-running a playbook should only make changes if system state has drifted from desired state.

---

### First Run

![First Run](<./images/Screenshot 2026-02-26 163842.png>)

**Analysis:**
-  **9 tasks changed** (yellow)
- System was in initial state
- All packages installed
- Docker service started
- User added to group

---

### Second Run

![Second Run](<./images/Screenshot 2026-02-26 163855.png>)

**Analysis:**
- **0 tasks changed** (green "ok")
- Desired state already achieved
- No unnecessary operations
- Idempotency

---

### What Changed First Time?

| Task | Why Changed? |
|------|--------------|
| **Update apt cache** | Cache was outdated |
| **Install packages** | Packages not installed |
| **Add GPG key** | Key didn't exist |
| **Add repository** | Repository not configured |
| **Install Docker** | Docker not present |
| **Start Docker service** | Service not running |
| **Add user to group** | User not in docker group |
| **Install Docker SDK** | Python package missing |

---

### Why Nothing Changed Second Time?

Ansible **detected current state = desired state** for all resources:

- Packages already installed (`state=present` satisfied)
- Docker service already running (`state=started` satisfied)
- User already in group (`groups: docker` satisfied)
- Repository already exists

**Key Insight:** Ansible compares current vs desired state **before** applying changes.

---

### What Makes Tasks Idempotent?

**1. State-based modules:**
```yaml
apt:
  name: docker-ce
  state: present  # ← Declarative, not imperative
```

**2. Service management:**
```yaml
service:
  name: docker
  state: started  # ← Starts only if stopped
```

**3. User management:**
```yaml
user:
  name: ubuntu
  groups: docker
  append: yes  # ← Doesn't remove other groups
```

**4. Conditional operations:**
```yaml
apt:
  update_cache: yes
  cache_valid_time: 3600  # ← Skip if cache fresh
```

---

## 4. Ansible Vault Usage

### How Credentials Are Stored Securely

**Encrypted file:**

```
inventory/group_vars/all.yml
```

**Created with:**

```bash
ansible-vault create inventory/group_vars/all.yml
```

**Encrypted content:**

![Encrypted content](<./images/Screenshot 2026-02-26 192129.png>)

---

### Vault Password Management Strategy

**Password file:** `.vault_pass`

```bash
# Create password file (do ONCE)
echo "your-secure-password" > .vault_pass
chmod 600 .vault_pass
```

**Added to `.gitignore`:**

```
# Ansible
.vault_pass
*.retry
__pycache__/
```

**Usage with playbooks:**

**Option 1: Prompt for password**
```bash
ansible-playbook playbooks/deploy.yml --ask-vault-pass
```

---

### Why Ansible Vault is Important

1. **Prevents credential leaks** — No plaintext secrets in git
2. **Safe version control** — Encrypted files can be committed
3. **Team collaboration** — Share playbooks without exposing secrets
4. **Compliance** — Meets security best practices
5. **Audit trail** — Track changes to encrypted files

---

## 5. Deployment Verification

### Deployment Execution

![Deployment Run](<./images/Screenshot 2026-02-26 170120.png>)


### Container Status

![Container Status](<./images/Screenshot 2026-02-26 170411.png>)


### Health Check and Main Endpoint Verification

![Health Check Status](<./images/Screenshot 2026-02-26 170552.png>)


### Handler Execution

Handlers were **not triggered** in this deployment because:
- Container didn't exist before (no config change)
- First deployment uses `state=started`

**Handlers would trigger when:**
- Updating image tag
- Changing environment variables
- Modifying port mappings

---

## 7. Key Decisions

### Why use roles instead of plain playbooks?

Roles provide **modular architecture** with clear **separation of concerns**. Each role has a single responsibility:
- `common` → system packages
- `docker` → Docker installation  
- `app_deploy` → application deployment


### How do roles improve reusability?

Roles **encapsulate logic and variables**, making them portable across projects:

1. **Same role, different projects:**
   - `docker` role works on any Ubuntu server
   - No code duplication

2. **Override variables per environment:**
   ```yaml
   # dev environment
   docker_user: devuser
   
   # prod environment
   docker_user: ubuntu
   ```

3. **Share via Ansible Galaxy:**
   - Publish roles for community
   - Import roles from others

4. **Version control roles independently:**
   - Update docker role without touching app_deploy
   - Clear change history

---

### What makes a task idempotent?

A task is **idempotent** when:
> Running it multiple times produces the same final state, regardless of initial state.


### How do handlers improve efficiency?

**Answer:**

Handlers **execute only when notified** and **only once per playbook run**, preventing unnecessary service restarts:


### Why is Ansible Vault necessary?

Ansible Vault is **essential for secure credential (encrypted at rest) management**:

---

## 8. Challenges

### Challenge 1: WSL2 File Permissions

**Problem:**
```
[WARNING]: Ansible is being run in a world writable directory
```

**Cause:** Windows filesystem (`/mnt/c/`) has open permissions incompatible with Ansible security requirements.

**Solution:** Copied project to WSL native filesystem:
```bash
cp -r /mnt/c/.../ansible ~/ansible-lab05
```

**Learning:** Always work in WSL native filesystem for Ansible projects.
