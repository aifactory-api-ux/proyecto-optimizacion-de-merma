# DEVELOPMENT PLAN: Proyecto optimizacion de merma

## 1. ARCHITECTURE OVERVIEW

**System Components:**
- **Backend (Python 3.11 + FastAPI):** Monolithic modular API, implements all business logic, data ingestion, forecasting, alerting, recommendations, and user authentication.
- **Database (PostgreSQL 15):** Stores all structured data (users, products, inventory, sales, waste, predictions, alerts).
- **Frontend (React 18 + TypeScript):** Dashboard for visualization, alerting, recommendations, and user interaction.
- **Infrastructure (Docker, AWS EC2/RDS/S3):** Containerized deployment, cloud storage for historical datasets, managed DB, and scalable compute.

**Folder Structure:**
```
project-root/
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── alerts.py
│   │   │   ├── waste.py
│   │   │   ├── demand.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── cache.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── waste.py
│   │   │   ├── alert.py
│   │   │   ├── demand.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── dashboard.py
│   │   │   ├── waste.py
│   │   │   ├── alert.py
│   │   │   ├── demand.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── dashboard_service.py
│   │   │   ├── waste_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── demand_service.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── base.py
│   │   ├── aws/
│   │   │   ├── s3.py
│   │   ├── ingestion/
│   │   │   ├── pos_ingest.py
│   │   │   ├── inventory_ingest.py
│   │   ├── tasks/
│   │   │   ├── nightly.py
│   ├── shared/
│   │   ├── utils.py
│   │   ├── constants.py
├── frontend/
│   ├── Dockerfile
│   ├── public/
│   │   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   ├── index.ts
│   │   │   ├── auth.ts
│   │   │   ├── dashboard.ts
│   │   │   ├── waste.ts
│   │   │   ├── alerts.ts
│   │   │   ├── demand.ts
│   │   ├── hooks/
│   │   │   ├── useAuth.ts
│   │   │   ├── useDashboard.ts
│   │   │   ├── useWaste.ts
│   │   │   ├── useAlerts.ts
│   │   │   ├── useDemand.ts
│   │   ├── components/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── WasteChart.tsx
│   │   │   ├── WasteByProductTable.tsx
│   │   │   ├── AlertsList.tsx
│   │   │   ├── DemandPredictionCard.tsx
│   │   ├── types/
│   │   │   ├── index.ts
│   │   ├── utils/
│   │   │   ├── format.ts
│   │   ├── styles/
│   │   │   ├── theme.ts
│   │   │   ├── global.css
├── docker-compose.yml
├── .env.example
├── .gitignore
├── .dockerignore
├── run.sh
├── README.md
├── docs/
│   ├── architecture.md
```

**Key Models & APIs:**
- User, Product, Store, Inventory, Sales, Waste, DemandPrediction, Alert (see erDiagram in context)
- REST API endpoints as per SPEC.md §3 (auth, dashboard, alerts, waste, demand)

## 2. ACCEPTANCE CRITERIA

1. The system ingests and consolidates historical sales/inventory/waste data for 3 pilot stores, storing normalized data in PostgreSQL and S3, with logs and error handling.
2. The backend exposes all required REST endpoints (`/auth/login`, `/dashboard/metrics`, `/alerts`, `/waste/by-product`, `/waste/trend`, `/demand/prediction`) with correct request/response contracts, JWT authentication, and RBAC enforced.
3. The frontend dashboard displays metrics, trends, alerts, and recommendations for authorized users, with functional/basic UI (Assumption: functional/basic UI is sufficient unless otherwise specified).
4. The system generates demand predictions and overstock alerts daily, and recommendations are visible in the dashboard.
5. The application is fully containerized, deployable via `./run.sh`, with all services healthy, and accessible at the printed URL.
6. All environment variables are validated on startup; missing critical variables cause a startup failure.
7. Healthcheck endpoints are available for backend and frontend containers.
8. No manual steps are required post-clone; the system runs end-to-end with `./run.sh`.

## TEAM SCOPE (MANDATORY — PARSED BY THE PIPELINE)

- **Role:** role-tl (technical_lead)
- **Role:** role-be (backend_developer)
- **Role:** role-fe (frontend_developer)
- **Role:** role-devops (devops_support)

---

## 3. EXECUTABLE ITEMS

---

### ITEM 1: Foundation — shared types, interfaces, DB schemas, config

**Goal:** Create all shared code and configuration for backend and frontend. Includes: all Pydantic/SQLAlchemy models, TypeScript interfaces, shared config, utility functions, and DB schema.

**Files to create:**
- backend/app/models/user.py
- backend/app/models/waste.py
- backend/app/models/alert.py
- backend/app/models/demand.py
- backend/app/schemas/auth.py
- backend/app/schemas/dashboard.py
- backend/app/schemas/waste.py
- backend/app/schemas/alert.py
- backend/app/schemas/demand.py
- backend/app/core/config.py
- backend/app/core/security.py
- backend/app/core/cache.py
- backend/app/db/base.py
- backend/app/db/session.py
- backend/shared/utils.py
- backend/shared/constants.py
- frontend/src/types/index.ts
- frontend/src/utils/format.ts

**Dependencies:** None

**Validation:** All models and config modules importable without error; running `python -m app.models.user` and `tsc --noEmit` in frontend passes without errors.

**Role:** role-tl (technical_lead)

---

### ITEM 2: Backend — API endpoints, ingestion, forecasting, alerting, recommendations

**Goal:** Implement all backend business logic and REST API endpoints as per SPEC.md §3:
- User authentication (JWT, RBAC)
- Data ingestion (POS, inventory, waste) and scheduled consolidation
- Demand prediction (basic model, daily batch)
- Overstock detection and alert generation
- Recommendation engine (reponer, no reponer, descuento, mover a bodega)
- Dashboard metrics aggregation
- All endpoints: `/auth/login`, `/dashboard/metrics`, `/alerts`, `/waste/by-product`, `/waste/trend`, `/demand/prediction`
- S3 integration for historical datasets
- Healthcheck endpoint

**Files to create:**
- backend/main.py
- backend/app/api/auth.py
- backend/app/api/dashboard.py
- backend/app/api/alerts.py
- backend/app/api/waste.py
- backend/app/api/demand.py
- backend/app/services/auth_service.py
- backend/app/services/dashboard_service.py
- backend/app/services/waste_service.py
- backend/app/services/alert_service.py
- backend/app/services/demand_service.py
- backend/app/aws/s3.py
- backend/app/ingestion/pos_ingest.py
- backend/app/ingestion/inventory_ingest.py
- backend/app/tasks/nightly.py
- backend/Dockerfile

**Dependencies:** Item 1

**Validation:** 
- `docker build -t merma-backend ./backend` succeeds
- `docker run -e ... merma-backend` starts and `/health` returns 200
- All REST endpoints respond with correct contract and RBAC enforced

**Role:** role-be (backend_developer)

---

### ITEM 3: Frontend — Dashboard, metrics, alerts, recommendations

**Goal:** Implement the React dashboard for visualization and user interaction:
- Login form (JWT)
- Dashboard with metrics, trends, demand prediction, alerts, recommendations
- Waste trend chart, waste by product table, alerts list, demand prediction card
- API integration (axios) for all endpoints
- State management via hooks
- Healthcheck endpoint
- Functional/basic UI (Assumption: functional/basic UI is sufficient unless otherwise specified)

**Files to create:**
- frontend/public/index.html
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/api/index.ts
- frontend/src/api/auth.ts
- frontend/src/api/dashboard.ts
- frontend/src/api/waste.ts
- frontend/src/api/alerts.ts
- frontend/src/api/demand.ts
- frontend/src/hooks/useAuth.ts
- frontend/src/hooks/useDashboard.ts
- frontend/src/hooks/useWaste.ts
- frontend/src/hooks/useAlerts.ts
- frontend/src/hooks/useDemand.ts
- frontend/src/components/LoginForm.tsx
- frontend/src/components/Dashboard.tsx
- frontend/src/components/WasteChart.tsx
- frontend/src/components/WasteByProductTable.tsx
- frontend/src/components/AlertsList.tsx
- frontend/src/components/DemandPredictionCard.tsx
- frontend/src/styles/theme.ts
- frontend/src/styles/global.css
- frontend/Dockerfile

**Dependencies:** Item 1

**Validation:** 
- `docker build -t merma-frontend ./frontend` succeeds
- `docker run -e ... merma-frontend` starts and `/health` returns 200
- UI loads, login works, dashboard displays metrics, alerts, recommendations

**Role:** role-fe (frontend_developer)

---

### ITEM 4: Infrastructure & Deployment

**Goal:** Provide complete container orchestration and documentation for local and cloud deployment:
- Docker Compose for backend, frontend, PostgreSQL, Redis
- Healthchecks and startup order
- Environment variable templates
- Run script for local setup
- Documentation and architecture overview

**Files to create:**
- docker-compose.yml
- .env.example
- .gitignore
- .dockerignore
- run.sh
- README.md
- docs/architecture.md

**Dependencies:** Items 1, 2, 3

**Validation:** 
- `./run.sh` builds and starts all services, waits for health, prints access URL
- All endpoints and UI accessible at printed URL
- No manual steps required post-clone

**Role:** role-devops (devops_support)

---