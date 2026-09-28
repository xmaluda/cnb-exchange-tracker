# ČNB Currency Rate Monitor & API Microservice

An automated backend microservice that ingests daily exchange rates from the official Czech National Bank (ČNB) REST API, persists the structured records in a PostgreSQL database, and exposes custom REST endpoints alongside a lightweight, server-rendered web dashboard.

## Architecture Overview

The system is deployed via Docker Compose using two isolated containers communicating across an internal Docker bridge network:

```text
                  [ Web Browser / Client ]
                             │
                      Port 8000 (HTTP)
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ Container: cnb_api_app (FastAPI + Uvicorn)             │
  │  • Automated ingestion worker (ČNB REST API client)    │
  │  • Custom REST API endpoints (/api/rates/latest)       │
  │  • Interactive OpenAPI docs (/docs)                    │
  │  • Server-rendered dashboard (Jinja2 + Native CSS)     │
  └──────────────────────────┬─────────────────────────────┘
                             │
             Docker Network (Hostname: db, Port: 5432)
                             │
                             ▼
  ┌────────────────────────────────────────────────────────┐
  │ Container: cnb_postgres_db (PostgreSQL 16 Alpine)     │
  │  • Relational database: 'forex'                        │
  │  • Named volume persistence: 'postgres_data'           │
  │  • Composite unique constraints & indexing             │
  └────────────────────────────────────────────────────────┘
```

## Key Features

* **Automated Data Ingestion:** Fetches daily FX data via HTTP GET from `api.cnb.cz`, parsing target currencies (`EUR`, `USD`, `GBP`).
* **Relational Storage & Idempotency:** Implements PostgreSQL with composite unique constraints (`rate_date`, `currency_code`) using `ON CONFLICT DO NOTHING` to prevent duplicates.
* **REST API & Swagger:** Auto-generated interactive API documentation at `/docs` compliant with OpenAPI specifications.
* **Zero-Dependency Dashboard:** Clean, responsive UI rendered via Jinja2 with lightweight, embedded CSS (no external JS/CSS frameworks needed).
* **Production-Ready Containerization:** Multi-container orchestration, persistent volumes, environment isolation, and database healthchecks.

## Project Structure

```text
cnb-exchange-tracker/
├── app/
│   ├── templates/
│   │   └── index.html       # Web dashboard template (HTML + Native CSS)
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI routes and dashboard handler
│   ├── database.py          # PostgreSQL pool connection and queries
│   └── collector.py         # External ČNB REST API ingestion logic
├── Dockerfile               # Python environment build definition
├── docker-compose.yml       # Multi-service composition (App + Database)
├── requirements.txt         # Pinned application dependencies
├── .gitignore               # Ignored local files, pycache, volumes
└── README.md                # Project documentation
```

## Database Schema

```sql
CREATE TABLE IF NOT EXISTS exchange_rates (
    id SERIAL PRIMARY KEY,
    rate_date DATE NOT NULL,
    currency_code VARCHAR(3) NOT NULL,
    rate NUMERIC(10, 4) NOT NULL,
    amount INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_rate_per_day UNIQUE (rate_date, currency_code)
);

CREATE INDEX IF NOT EXISTS idx_rates_date ON exchange_rates(rate_date);
CREATE INDEX IF NOT EXISTS idx_rates_currency ON exchange_rates(currency_code);
```

## Quickstart (Docker Compose)

### Prerequisites
* Docker Desktop or Docker Engine + Compose installed.

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/cnb-exchange-tracker.git
cd cnb-exchange-tracker
```

### 2. Launch the services
```bash
docker compose up --build
```

The application will:
1. Boot and verify the PostgreSQL container via built-in healthchecks.
2. Initialize database tables automatically.
3. Ingest the latest rates from the ČNB API.
4. Start the web server at port `8000`.

## Endpoints & Usage

| Route | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Responsive web dashboard displaying current rates |
| `/docs` | `GET` | Interactive Swagger UI API playground |
| `/api/rates/latest` | `GET` | JSON payload of latest rates stored in PostgreSQL |
| `/api/rates/history/{code}` | `GET` | Historical exchange rate trend for target currency |

### Sample JSON Output (`/api/rates/latest`)
```json
[
  {
    "currency_code": "EUR",
    "rate": 25.245,
    "amount": 1,
    "rate_date": "2026-09-28"
  },
  {
    "currency_code": "USD",
    "rate": 22.810,
    "amount": 1,
    "rate_date": "2026-09-28"
  }
]
```

## Stopping the Application

To stop containers while preserving database volume records:
```bash
docker compose down
```

To purge the containers and erase all database volume records:
```bash
docker compose down -v
```

## Author
* **Matyáš Maľuda**
* Student of IT & Information Systems Administration at PEF MENDELU
