# Lab 17 — Cloudflare Workers (WORKERS.md)

## Deployment Summary
- **Worker URL:** https://edge-api.s-palkina.workers.dev
- **Main routes:**
  - `/` – basic app info
  - `/health` – health check
  - `/edge` – edge metadata from `request.cf`
  - `/counter` – KV-backed visit counter
- **Configuration used:**
  - `APP_NAME` and `COURSE_NAME` via `wrangler.jsonc` vars
  - `API_TOKEN`, `ADMIN_EMAIL` as Wrangler secrets
  - `SETTINGS` KV namespace binding

## Evidence
- Cloudflare dashboard (metrics + bindings):  
  ![alt text](<Screenshot 2026-05-10 222021.png>)

- Deployment + deployments list (terminal):  
  ![alt text](<Screenshot 2026-05-10 210424-1.png>)

- Example `/edge` JSON response
![alt text](<Screenshot 2026-05-10 210424.png>)

- Logs: viewed with `npx wrangler tail` after adding `console.log`.
![alt text](<Screenshot 2026-05-10 213526.png>)

- Persistant
![alt text](<Screenshot 2026-05-10 213242.png>)
![alt text](<Screenshot 2026-05-10 213254.png>)


## Edge Execution Notes
Workers execute at Cloudflare’s edge network automatically, close to the client.  
There is no “deploy to N regions” step because Workers are globally distributed by default.

## Routing Concepts
- **workers.dev**: default public URL for quick deployment.
- **Routes**: attach a Worker to traffic of an existing Cloudflare zone.
- **Custom Domains**: make the Worker serve as the origin for a domain/subdomain.

## Configuration & Persistence
- **Vars** (plaintext): stored in `wrangler.jsonc` — safe for non-secrets only.
- **Secrets**: set via Wrangler, never stored in Git.
- **KV Namespace**: persistent key-value storage; `/counter` proves values survive redeploy.

## Observability & Operations
- **Logs**: `npx wrangler tail` shows `console.log` entries.
- **Metrics**: viewed in dashboard (requests, errors, CPU time).
- **Deployments**: `npx wrangler deployments list` shows version history.

### Rollback (described)
If needed, rollback to a previous version can be done with:
```bash
npx wrangler rollback
```
This reverts the Worker to an earlier deployment in the history.

## Kubernetes vs Cloudflare Workers Comparison

| Aspect | Kubernetes | Cloudflare Workers |
|--------|------------|--------------------|
| Setup complexity | High (clusters, nodes, networking) | Low (CLI + deploy) |
| Deployment speed | Slower (build + registry + rollout) | Fast (seconds) |
| Global distribution | Manual regions | Built-in global edge |
| Cost (for small apps) | Higher baseline | Very low / free tier |
| State/persistence model | Pods + DB/cache | KV / Durable Objects |
| Control/flexibility | Full control | Limited runtime |
| Best use case | Complex services, long-running workloads | Lightweight APIs, edge logic |

## When to Use Each
- **Kubernetes**: complex systems, custom runtimes, long-running services, advanced networking.
- **Workers**: fast global APIs, lightweight HTTP logic, edge caching, low-latency needs.

**Recommendation:** Use Workers for small, globally distributed APIs. Use Kubernetes when full infrastructure control is required.

## Reflection
- **Easier than Kubernetes:** setup, deploy speed, global distribution.
- **More constrained:** limited runtime, no Docker.
- **What changed:** Workers run in a serverless edge runtime, so you design for short-lived requests and platform bindings instead of containers.