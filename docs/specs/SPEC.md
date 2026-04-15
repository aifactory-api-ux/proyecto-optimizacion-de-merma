# SPEC.md

## 1. TECHNOLOGY STACK

- **Backend**
  - Python 3.11
  - FastAPI 0.110.0
  - Pydantic 2.6.4
  - SQLAlchemy 2.0.29
  - asyncpg 0.29.0
  - psycopg2-binary 2.9.9
  - Redis 5.0.3 (for caching, via redis-py 5.0.3)
  - boto3 1.34.84 (AWS S3 integration)
  - python-jose 3.3.0 (JWT)
  - uvicorn 0.29.0

- **Database**
  - PostgreSQL 15

- **Frontend**
  - React 18.2.0
  - TypeScript 5.4.2
  - react-router-dom 6.23.0
  - axios 1.6.7
  - recharts 2.7.2 (for charts)
  - @mui/material 5.15.8 (Material UI)

- **Infrastructure**
  - Docker 26.1.3
  - docker-compose 2.27.0
  - AWS EC2 (Ubuntu 22.04 LTS)
  - AWS RDS PostgreSQL 15
  - AWS S3

## 2. DATA CONTRACTS

### Python (Pydantic Models)

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str

class WasteMetric(BaseModel):
    date: datetime
    product_id: int
    product_name: str
    waste_quantity: float
    waste_cost: float

class DashboardMetricsResponse(BaseModel):
    total_waste_quantity: float
    total_waste_cost: float
    waste_by_product: List[WasteMetric]
    waste_trend: List[WasteMetric]
    alerts: List[str]
    demand_prediction: Optional[float] = None

class Alert(BaseModel):
    id: int
    created_at: datetime
    message: str
    severity: str  # "info", "warning", "critical"
```

### TypeScript (Frontend Interfaces)

```typescript
export interface UserLoginRequest {
  username: string;
  password: string;
}

export interface UserLoginResponse {
  access_token: string;
  token_type: string;
}

export interface WasteMetric {
  date: string; // ISO 8601
  product_id: number;
  product_name: string;
  waste_quantity: number;
  waste_cost: number;
}

export interface DashboardMetricsResponse {
  total_waste_quantity: number;
  total_waste_cost: number;
  waste_by_product: WasteMetric[];
  waste_trend: WasteMetric[];
  alerts: string[];
  demand_prediction?: number;
}

export interface Alert {
  id: number;
  created_at: string; // ISO 8601
  message: string;
  severity: "info" | "warning" | "critical";
}
```

## 3. API ENDPOINTS

### POST /auth/login

- **Request Body:** `UserLoginRequest`
- **Response:** `UserLoginResponse`
- **Description:** Authenticate user and return JWT token.

### GET /dashboard/metrics

- **Headers:** `Authorization: Bearer <token>`
- **Response:** `DashboardMetricsResponse`
- **Description:** Returns consolidated waste metrics, trends, alerts, and demand prediction for dashboard.

### GET /alerts

- **Headers:** `Authorization: Bearer <token>`
- **Response:** `List[Alert]`
- **Description:** Returns all active alerts.

### GET /waste/by-product

- **Headers:** `Authorization: Bearer <token>`
- **Query Params:** `start_date: string (ISO 8601)`, `end_date: string (ISO 8601)`
- **Response:** `List[WasteMetric]`
- **Description:** Returns waste metrics grouped by product for the given date range.

### GET /waste/trend

- **Headers:** `Authorization: Bearer <token>`
- **Query Params:** `product_id: int`, `start_date: string (ISO 8601)`, `end_date: string (ISO 8601)`
- **Response:** `List[WasteMetric]`
- **Description:** Returns time series of waste for a product.

### GET /demand/prediction

- **Headers:** `Authorization: Bearer <token>`
- **Query Params:** `product_id: int`, `date: string (ISO 8601)`
- **Response:** `{ demand_prediction: float }`
- **Description:** Returns demand prediction for a product on a given date.

## 4. FILE STRUCTURE

```
.
├── docker-compose.yml                # Orchestrates backend, frontend, db, redis
├── .env.example                      # Template for environment variables
├── .gitignore                        # Git ignore rules
├── README.md                         # Project documentation
├── run.sh                            # Root startup script
├── backend/
│   ├── Dockerfile                    # Backend Docker build
│   ├── main.py                       # FastAPI entrypoint
│   ├── app/
│   │   ├── __init__.py               # App package init
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # /auth/login endpoint
│   │   │   ├── dashboard.py          # /dashboard/metrics endpoint
│   │   │   ├── alerts.py             # /alerts endpoint
│   │   │   ├── waste.py              # /waste endpoints
│   │   │   ├── demand.py             # /demand endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Settings, env var loading
│   │   │   ├── security.py           # JWT, password hashing
│   │   │   ├── cache.py              # Redis integration
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User SQLAlchemy model
│   │   │   ├── waste.py              # WasteRecord, WasteMetric models
│   │   │   ├── alert.py              # Alert model
│   │   │   ├── demand.py             # DemandPrediction model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py               # UserLoginRequest, UserLoginResponse
│   │   │   ├── dashboard.py          # DashboardMetricsResponse
│   │   │   ├── waste.py              # WasteMetric
│   │   │   ├── alert.py              # Alert
│   │   │   ├── demand.py             # DemandPrediction
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py       # Auth logic
│   │   │   ├── dashboard_service.py  # Metrics aggregation
│   │   │   ├── waste_service.py      # Waste logic
│   │   │   ├── alert_service.py      # Alert logic
│   │   │   ├── demand_service.py     # Prediction logic
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py            # DB session management
│   │   │   ├── base.py               # Declarative base
│   │   ├── aws/
│   │   │   ├── __init__.py
│   │   │   ├── s3.py                 # S3 integration
│   │   ├── ingestion/
│   │   │   ├── __init__.py
│   │   │   ├── pos_ingest.py         # POS data ingestion
│   │   │   ├── inventory_ingest.py   # Inventory system ingestion
│   │   ├── tasks/
│   │   │   ├── __init__.py
│   │   │   ├── nightly.py            # Nightly ingestion/processing
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── utils.py                  # Shared utilities
│   │   ├── constants.py              # Shared constants
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_dashboard.py
│   │   ├── test_waste.py
│   │   ├── test_alerts.py
│   │   ├── test_demand.py
├── frontend/
│   ├── Dockerfile                    # Frontend Docker build
│   ├── public/
│   │   ├── index.html                # HTML entrypoint
│   ├── src/
│   │   ├── main.tsx                  # React entrypoint
│   │   ├── App.tsx                   # App root
│   │   ├── api/
│   │   │   ├── index.ts              # API client (axios)
│   │   │   ├── auth.ts               # Auth API
│   │   │   ├── dashboard.ts          # Dashboard API
│   │   │   ├── waste.ts              # Waste API
│   │   │   ├── alerts.ts             # Alerts API
│   │   │   ├── demand.ts             # Demand API
│   │   ├── hooks/
│   │   │   ├── useAuth.ts            # Auth state
│   │   │   ├── useDashboard.ts       # Dashboard state
│   │   │   ├── useWaste.ts           # Waste state
│   │   │   ├── useAlerts.ts          # Alerts state
│   │   │   ├── useDemand.ts          # Demand prediction state
│   │   ├── components/
│   │   │   ├── LoginForm.tsx         # Login form
│   │   │   ├── Dashboard.tsx         # Dashboard main
│   │   │   ├── WasteChart.tsx        # Waste trend chart
│   │   │   ├── WasteByProductTable.tsx # Waste by product table
│   │   │   ├── AlertsList.tsx        # Alerts display
│   │   │   ├── DemandPredictionCard.tsx # Demand prediction
│   │   ├── types/
│   │   │   ├── index.ts              # All TypeScript interfaces
│   │   ├── utils/
│   │   │   ├── format.ts             # Formatting helpers
│   │   ├── styles/
│   │   │   ├── theme.ts              # MUI theme
│   │   │   ├── global.css            # Global styles
│   ├── tests/
│   │   ├── LoginForm.test.tsx
│   │   ├── Dashboard.test.tsx
│   │   ├── WasteChart.test.tsx
│   │   ├── AlertsList.test.tsx
│   │   ├── DemandPredictionCard.test.tsx
```

## 5. ENVIRONMENT VARIABLES

| Name                       | Type   | Description                                      | Example Value                      |
|----------------------------|--------|--------------------------------------------------|------------------------------------|
| POSTGRES_HOST              | str    | PostgreSQL hostname                              | db                                |
| POSTGRES_PORT              | int    | PostgreSQL port                                  | 5432                              |
| POSTGRES_DB                | str    | PostgreSQL database name                         | merma_db                          |
| POSTGRES_USER              | str    | PostgreSQL username                              | merma_user                        |
| POSTGRES_PASSWORD          | str    | PostgreSQL password                              | strongpassword                    |
| REDIS_HOST                 | str    | Redis hostname                                   | redis                             |
| REDIS_PORT                 | int    | Redis port                                       | 6379                              |
| AWS_ACCESS_KEY_ID          | str    | AWS access key for S3                            | AKIA...                           |
| AWS_SECRET_ACCESS_KEY      | str    | AWS secret key for S3                            | ...                               |
| AWS_S3_BUCKET              | str    | S3 bucket for historical datasets                | merma-datasets                    |
| JWT_SECRET_KEY             | str    | Secret key for JWT signing                       | supersecretkey                    |
| JWT_ALGORITHM              | str    | JWT algorithm                                    | HS256                             |
| JWT_ACCESS_TOKEN_EXPIRE_MINUTES | int | JWT expiration in minutes                        | 60                                |
| BACKEND_CORS_ORIGINS       | str    | Comma-separated allowed CORS origins             | http://localhost:5173             |
| LOG_LEVEL                  | str    | Logging level                                    | info                              |
| ENVIRONMENT                | str    | Deployment environment                           | development                       |

## 6. IMPORT CONTRACTS

### Backend

- `from app.schemas.auth import UserLoginRequest, UserLoginResponse`
- `from app.schemas.dashboard import DashboardMetricsResponse`
- `from app.schemas.waste import WasteMetric`
- `from app.schemas.alert import Alert`
- `from app.schemas.demand import DemandPrediction`
- `from app.services.auth_service import authenticate_user, create_access_token`
- `from app.services.dashboard_service import get_dashboard_metrics`
- `from app.services.waste_service import get_waste_by_product, get_waste_trend`
- `from app.services.alert_service import get_active_alerts`
- `from app.services.demand_service import get_demand_prediction`
- `from app.core.config import settings`
- `from app.core.security import verify_password, get_password_hash, decode_jwt_token`
- `from app.core.cache import get_redis_client, cache_data, get_cached_data`
- `from app.aws.s3 import download_historical_dataset, upload_dataset`
- `from app.db.session import get_db`
- `from app.models.user import User`
- `from app.models.waste import WasteRecord, WasteMetric`
- `from app.models.alert import Alert`
- `from app.models.demand import DemandPrediction`
- `from shared.utils import parse_date, to_camel_case`
- `from shared.constants import WASTE_SEVERITY_LEVELS`

### Frontend

- `import { UserLoginRequest, UserLoginResponse, WasteMetric, DashboardMetricsResponse, Alert } from '../types'`
- `import { useAuth } from '../hooks/useAuth'`
- `import { useDashboard } from '../hooks/useDashboard'`
- `import { useWaste } from '../hooks/useWaste'`
- `import { useAlerts } from '../hooks/useAlerts'`
- `import { useDemand } from '../hooks/useDemand'`
- `import { login, fetchDashboardMetrics, fetchWasteByProduct, fetchWasteTrend, fetchAlerts, fetchDemandPrediction } from '../api'`
- `import { formatDate, formatCurrency } from '../utils/format'`
- `import { ThemeProvider } from '@mui/material/styles'`
- `import { WasteChart } from '../components/WasteChart'`
- `import { WasteByProductTable } from '../components/WasteByProductTable'`
- `import { AlertsList } from '../components/AlertsList'`
- `import { DemandPredictionCard } from '../components/DemandPredictionCard'`

## 7. FRONTEND STATE & COMPONENT CONTRACTS

### Shared State Primitives (React Hooks)

- `useAuth() → { user: UserLoginResponse | null, login: (data: UserLoginRequest) => Promise<void>, logout: () => void, loading: boolean, error: string | null }`
- `useDashboard() → { metrics: DashboardMetricsResponse | null, loading: boolean, error: string | null, refresh: () => Promise<void> }`
- `useWaste() → { wasteByProduct: WasteMetric[], wasteTrend: WasteMetric[], loading: boolean, error: string | null, fetchByProduct: (start: string, end: string) => Promise<void>, fetchTrend: (productId: number, start: string, end: string) => Promise<void> }`
- `useAlerts() → { alerts: Alert[], loading: boolean, error: string | null, refresh: () => Promise<void> }`
- `useDemand() → { demandPrediction: number | null, loading: boolean, error: string | null, fetchPrediction: (productId: number, date: string) => Promise<void> }`

### Reusable Components

- `LoginForm` props: `{ onSubmit: (data: UserLoginRequest) => void, loading: boolean, error: string | null }`
- `Dashboard` props: `{ metrics: DashboardMetricsResponse | null, loading: boolean, onRefresh: () => void }`
- `WasteChart` props: `{ data: WasteMetric[], loading: boolean }`
- `WasteByProductTable` props: `{ data: WasteMetric[], loading: boolean }`
- `AlertsList` props: `{ alerts: Alert[], loading: boolean }`
- `DemandPredictionCard` props: `{ demandPrediction: number | null, loading: boolean }`

## 8. FILE EXTENSION CONVENTION

- **Frontend files:** `.tsx` (all React components and hooks)
- **Project language:** TypeScript (all frontend files use `.ts`/`.tsx`)
- **Entry point:** `/src/main.tsx` (as referenced in `public/index.html` via `<script src="/src/main.tsx">`)
- **Backend files:** `.py` (Python 3.11)
- **No JavaScript or `.jsx` files are used anywhere in the project.**

---

**PORT TABLE**

| Service   | Listening Port | Path              |
|-----------|---------------|-------------------|
| backend   | 8000          | backend/          |

**SHARED MODULES**

| Shared path      | Imported by services |
|------------------|---------------------|
| backend/shared/  | backend             |