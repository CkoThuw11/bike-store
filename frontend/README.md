# 🚲 Bikeshop UI

Angular admin console for the Bike Store backend — manages brands, categories, products, stores, staff, stock, customers, and orders. Built with standalone components, Signals, and an MVVM pattern.

## 🔎 Project Snapshot

- **Framework:** Angular 17 (standalone components, no `NgModule`)
- **State:** Signals for component state; RxJS reserved for complex streams
- **Auth:** JWT bearer token via HTTP interceptor; the whole app shell is admin-only (see [Routing & Access](#-routing--access))
- **API access:** Same-origin relative paths (`apiUrl: ''`) — proxied to the backend, never called cross-origin
- **Containers:** Multi-stage Docker build → static bundle served by Nginx

## 🧱 Architecture

```text
View (template)
  ⬇ triggers action
ViewModel (component) — Signals hold state, handles UI logic
  ⬇ calls
Model (service) — HttpClient, data transformation
  ⬆ returns
View — updates via signal bindings, no manual change detection
```

Core rules:

- Components don't know what HTTP is — all API access goes through services in `core/`.
- Derived state is `computed()`, not recalculated in templates.
- No logic inside HTML templates.

Full conventions (naming, DO/DON'T rules, examples) live in [`../AGENT.md`](../AGENT.md) — read it before contributing.

## 🧰 Tech Stack

| Area | Technology |
| --- | --- |
| Framework | Angular 17, standalone components |
| State | Signals, RxJS |
| Styling | SCSS, Bootstrap 5 + Bootstrap Icons |
| HTTP | `HttpClient` with a bearer-token interceptor |
| Testing | Karma + Jasmine |
| Containers | Docker (multi-stage build) + Nginx |

## 📁 Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── core/            # Auth, API errors, interceptors, app shell/layout
│   │   ├── features/        # One folder per route: brands, products, orders, staffs, ...
│   │   ├── shared/          # Reusable UI (toast, drawer, confirm, command palette), state, types, utils
│   │   ├── app.routes.ts    # Route table + guards
│   │   └── app.config.ts    # App-level providers
│   ├── environments/        # apiUrl config (dev vs prod)
│   └── styles.scss          # Global styles + design tokens (CSS variables)
├── nginx.conf                # Serves the built app + proxies API routes to the backend container
├── proxy.conf.json           # Dev-server proxy → localhost:8000 (avoids CORS locally)
├── Dockerfile
└── angular.json
```

## 🚀 Run

### Dev server

```bash
npm install
ng serve
```

Navigate to `http://localhost:4200/`. Requests to `/auth`, `/brands`, `/products`, etc. are proxied to `http://localhost:8000` via `proxy.conf.json` — the backend must be running separately (see [`../backend/README.md`](../backend/README.md) or the root [`../README.md`](../README.md) for Docker Compose).

### Docker

Built as part of the root `docker-compose.yml` — see [`../README.md`](../README.md). The container runs a production build (`ng build`) served by Nginx on port 80 (mapped to `4200`), with `/auth`, `/brands`, `/categories`, etc. proxied server-side to the `backend` container. There is no live reload inside Docker; use the dev server above for active development.

### Build

```bash
ng build --configuration production
```

Output goes to `dist/bikeshop-ui/`.

### Tests

```bash
ng test                                            # watch mode
ng test --watch=false --browsers=ChromeHeadless    # CI-style single run
```

## 🔐 Routing & Access

Every route except `/login` and `/register` sits behind **both** `authGuard` and `adminGuard` — this console is admin-only. A valid but non-admin (`CUSTOMER`) token gets its session cleared and is redirected to `/login?reason=admin-only`. See `src/app/core/auth/guards.ts`.

| Path | Purpose |
| --- | --- |
| `/login`, `/register` | Public, redirect away if already authenticated |
| `/dashboard` | Landing page after login |
| `/brands`, `/categories`, `/products` | Catalog management |
| `/stores`, `/staffs`, `/stocks` | Operations |
| `/customers`, `/orders` (+ `create-order`) | Sales |
| `/profile`, `/settings` | Account |

## ⚠️ Known Notes

- `ng lint` is referenced in `../AGENT.md` and the CI pipeline description, but no ESLint config or `lint` script currently exists in this project — it is not actually runnable yet.
- `../AGENT.md` calls for a dedicated `src/app/theme` design-token folder; today, tokens live as CSS variables directly in `src/styles.scss` instead.
- `environment.apiUrl` is intentionally empty in both dev and prod — all API calls are same-origin, relying on the dev-server proxy (`proxy.conf.json`) or Nginx (`nginx.conf`) to route them to the backend. Do not hardcode an absolute backend URL here.
