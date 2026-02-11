# Lab 3 — Continuous Integration (CI/CD)

## 1. Overview

### Testing Framework: pytest
I chose **pytest** for unit testing because:
- **Simple syntax** — no boilerplate code, just `assert` statements
- **Powerful fixtures** — easy to create test clients and shared resources
- **Rich plugin ecosystem** — `pytest-cov` for coverage, integration with GitHub Actions
- **Industry standard** — widely used in Python DevOps projects

### Test Coverage
| Endpoint | What is tested |
|----------|----------------|
| `GET /` | ✓ Status code 200<br>✓ JSON content type<br>✓ All 5 sections (service, system, runtime, request, endpoints)<br>✓ Service name, version, framework<br>✓ System fields presence and types<br>✓ Uptime format and validity<br>✓ Request info (method, path) |
| `GET /health` | ✓ Status code 200<br>✓ Status = "healthy"<br>✓ Timestamp in ISO format<br>✓ Uptime seconds (positive integer) |
| Error handling | ✓ 404 Not Found response structure<br>✓ Error message format |

**Total tests:** 17 unit tests

### CI Workflow Triggers
The workflow runs on:
- **Push** to `master` and `lab03` branches
- **Pull request** targeting `master` branch

**Why?** 
- Push triggers ensure every commit is tested
- PR triggers catch issues before merging
- Lab03 branch is included for active development

### Versioning Strategy: Calendar Versioning (CalVer)
I chose **CalVer** with format `YYYY.MM` (e.g., `2025.02`)

**Rationale:**
- This is a **service**, not a library — breaking changes don't require SemVer
- Time-based versions are **easy to understand** and correlate with release dates
- Perfect for **continuous deployment** — new version every month
- Simple to implement in CI using `date` command

**Docker tags:**
- `spalkkina/devops-info-service:2026.02` — monthly version
- `spalkkina/devops-info-service:latest` — most recent build

---

## 2. Workflow Evidence

### Successful GitHub Actions Run
🔗 [Link to workflow run](https://github.com/angel-palkina/DevOps-Core-Course/actions/runs/21921911777)

### Tests Passing Locally
![alt text](screenshots/07-test-output.png)

### Docker Hub Image
🔗 [Docker Hub repository](https://hub.docker.com/r/spalkkina/devops-info-service)

| Tag | Size |
|----------|-----------|
| 2026.02 | 45.54 MB |
| latest | 45.54 MB |

### CI/CD Status

![CI](https://github.com/angel-palkina/DevOps-Core-Course/actions/workflows/python-ci.yml/badge.svg)

## Best Practices Implemented
- **Practice 1:** Dependency Caching

    What: Caching pip packages using actions/setup-python@v5 built-in cache

    Why: Speeds up workflow by ~104 seconds (no need to download packages every time)

    Before: 2m 05s → After: 1m 01s

- **Practice 2:** Job Dependencies (Fail Fast)

    What: Docker job has needs: test — only runs if tests pass

    Why: Prevents publishing broken images to Docker Hub

- **Practice 3:** Conditional Execution

    What: Docker job runs only on push, not on PRs

    Why: Avoid pushing images from temporary PR branches

- **Practice 4:** Security Scanning with Snyk

    What: Integrated Snyk to scan dependencies for vulnerabilities

    Why: Catch security issues before they reach production

    Snyk Results: no vulnerable paths found.

- **Practice 5:** Linting

    What: flake8 runs on every commit

    Why: Enforces code style consistency, catches syntax errors early

## Key Decisions

### Versioning Strategy: CalVer
**Why CalVer?** This is a web service, not a shared library. Users don't need to know about breaking changes via version numbers — they just consume the latest API. CalVer clearly communicates when the image was built, which is more useful for operations teams.

Alternative considered: SemVer — rejected because our app has no API consumers that pin versions.

### Docker Tags
What tags are created?

- YYYY.MM (e.g., 2026.02) — monthly version

- latest — points to the most recent build

**Why two tags?**

- latest is convenient for development and testing

- Date-based tag provides a stable reference for production rollbacks

### Workflow Triggers
Why push + PR?

- Push triggers ensure every commit is tested immediately

- PR triggers prevent merging broken code into master

Lab03 branch is included to test the workflow itself during development

### Test Coverage
What is tested?

- All happy paths (200 OK responses)

- Response structure and data types

- Error handlers (404)

- Helper functions

What is NOT tested?

- 500 error handler (requires mocking internal errors)

- Actual hostname value (changes per environment)

- IP address format (varies in CI)

