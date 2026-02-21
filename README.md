# Moniepoint Analytics API - My Solution to DreamDev 2026

This repository is a REST API that analyzes merchant activity data and exposes analytics endpoints.

## Author

Name: Silas Osunba  
Email: osunbasilas@gmail.com  

## Project Description

This project implements a REST Analytics API that processes merchant activity logs and exposes business insights across Moniepoint products (POS, AIRTIME, BILLS, CARD_PAYMENT, SAVINGS, MONIEBOOK, KYC). CSV data is imported into PostgreSQL and queried to serve the required analytics endpoints.

### Task 1: Import CSV data into a database — ✅ Achieved

As required, the application:

1. **Reads CSV files** from the `data/` directory (files named `data/activities_YYYYMMDD.csv`).
2. **Imports the data** into a database (PostgreSQL; e.g. local or [Neon](https://neon.tech)). The import script is `src/scripts/import_activities.py`; run it with `uv run python -m src.scripts.import_activities` after setting `DATABASE_URL` in `.env`.
3. **Uses the database** to serve all analytics endpoints (the API queries the imported data).

All CSV data has been imported into the chosen database (e.g. Neon) before the analytics API is used.

## Tech Stack

- Python (FastAPI)
- PostgreSQL
- SQLAlchemy

## Assumptions

- CSV files are placed in the `data/` directory with names `activities_YYYYMMDD.csv`.
- Rows with invalid `event_id` (non-UUID), missing required fields (`merchant_id`, `product`, `event_type`, `status`), or invalid `amount` are skipped during import; no row is updated.
- Empty `event_timestamp` is stored as NULL; analytics that depend on time (e.g. monthly active merchants) exclude these rows.
- Monetary values in responses use 2 decimal places; failure rates use 1 decimal place.
- The API is run on port 8080 as specified.
- I used psycopg2-binary (commonly used for rapid development and testing) instead of psycopg2. My primary reason that led to this choice is because it skip the requirement to configure complex database development libraries - which is considered in this code challenge, so as i could meet up with project's deadline.



## Setup Instructions

For a **step-by-step manual installation guide**, see [docs/INSTALL.md](docs/INSTALL.md).

### Prerequisites

- [UV](https://docs.astral.sh/uv/) (install: `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`)
- Python 3.10+
- PostgreSQL (e.g. 14+)
- CSV data in `data/activities_YYYYMMDD.csv`

### 1. Clone repository

```bash
git clone https://github.com/TolaniSilas/moniepoint-dreamdevs-analytics-api.git
cd moniepoint-dreamdevs-analytics-api
```

### 2. Create virtual environment and install dependencies (UV)

```bash
uv sync
```

This creates a `.venv` and installs dependencies from `pyproject.toml`. To use a specific Python: `uv sync --python 3.11`.

### 3. Create PostgreSQL database

```bash
# Using psql (adjust user if needed)
createdb moniepoint_analytics

# Or in psql:
# CREATE DATABASE moniepoint_analytics;
```

### 4. Configure environment

Copy the example env file and set your database URL:

```bash
cp .env.example .env
# Edit .env and set DATABASE_URL, e.g.:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moniepoint_analytics
```

### 5. Import CSV data

From the project root (with `data/` containing your CSV files):

```bash
uv run python -m src.scripts.import_activities
```

This creates the `activities` table and loads all `data/activities_*.csv` files. Malformed rows are skipped and counts are printed.

### 6. Start the API (run the analytics endpoints)

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080
```

The API will be available at `http://localhost:8080`. For a step-by-step run and test guide, see [docs/RUN_API.md](docs/RUN_API.md).

### 7. Test endpoints

```bash
curl http://localhost:8080/analytics/top-merchant
curl http://localhost:8080/analytics/monthly-active-merchants
curl http://localhost:8080/analytics/product-adoption
curl http://localhost:8080/analytics/kyc-funnel
curl http://localhost:8080/analytics/failure-rates
```

## API Endpoints (Port 8080)

| Endpoint | Description |
|----------|-------------|
| `GET /analytics/top-merchant` | Merchant with highest total successful transaction volume |
| `GET /analytics/monthly-active-merchants` | Unique merchants with at least one successful event per month |
| `GET /analytics/product-adoption` | Unique merchant count per product (sorted by count descending) |
| `GET /analytics/kyc-funnel` | KYC conversion funnel (documents submitted, verifications completed, tier upgrades) |
| `GET /analytics/failure-rates` | Failure rate per product (FAILED / (SUCCESS + FAILED)) × 100, excluding PENDING |

All responses are JSON.

## Repository structure

```
moniepoint-dreamdevs-analytics-api/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entrypoint
│   ├── core/                   # Config and shared dependencies
│   │   ├── config.py           # Settings (DB URL, data dir)
│   │   └── deps.py             # get_db and other deps
│   ├── db/                     # Database layer
│   │   └── base.py             # Engine, SessionLocal, Base
│   ├── models/                 # SQLAlchemy ORM models
│   │   └── activity.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   └── analytics.py
│   ├── services/               # Business logic
│   │   └── analytics.py        # AnalyticsService
│   ├── api/                    # HTTP layer
│   │   └── v1/
│   │       ├── router.py       # Aggregates v1 routes
│   │       └── endpoints/
│   │           └── analytics.py
│   └── scripts/                # CLI / one-off tasks
│       └── import_activities.py
├── data/
│   └── activities_YYYYMMDD.csv
├── pyproject.toml          # Project metadata & dependencies (UV)
├── .env.example
└── README.md
```
