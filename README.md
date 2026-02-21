# Moniepoint Analytics API – DreamDev 2026

REST API that analyzes merchant activity data and exposes five analytics endpoints. Built for the Moniepoint Growth & Intelligence use case: understanding merchant behavior across the product ecosystem.

---

## Author

**Name:** Silas Osunba  
**Email:** osunbasilas@gmail.com  

---

## For reviewers: quick setup

To run and test this submission:

1. **Clone** the repo and go into the project folder.
2. **Install dependencies** with UV: `uv sync`.
3. **Create a PostgreSQL database** (e.g. `moniepoint_analytics`) and set a password for your user.
4. **Configure environment:** copy `.env.example` to `.env` and set `DATABASE_URL` to your database (see [Configure environment](#4-configure-environment) below).
5. **Import CSV data:** `uv run python -m src.scripts.import_activities` (requires CSV files in `data/`).
6. **Start the API:** `uv run uvicorn src.main:app --host 0.0.0.0 --port 8080`.
7. **Test the endpoints** at `http://localhost:8080` (see [Test endpoints](#7-test-endpoints)).

The API runs on **port 8080** and returns JSON. Interactive docs: `http://localhost:8080/docs`.

---

## Project description

This project implements a REST Analytics API that processes merchant activity logs and exposes business insights across Moniepoint products (POS, AIRTIME, BILLS, CARD_PAYMENT, SAVINGS, MONIEBOOK, KYC). CSV data is imported into PostgreSQL and queried to serve the required analytics endpoints.

### Task 1: Import CSV data into a database

As required:

1. **Read** CSV files from the `data/` directory (filenames: `activities_YYYYMMDD.csv`).
2. **Import** the data into a database (PostgreSQL; local or cloud e.g. [Neon](https://neon.tech)). Import script: `src/scripts/import_activities.py`.
3. **Query** the database to serve all five analytics endpoints.

Data is loaded before the API is used; the API reads only from the database.

---

## Problem approach

The Growth and Intelligence Team at Moniepoint needs to understand merchant behavior across the full product ecosystem. Solving this means using their records (data) to get insights: how merchants behave, how the growth team can scale products, which areas need attention for better outcomes, and which areas are doing well so strategies can be refined.

The solution goes beyond implementation: it uses code to answer business questions and deliver actionable insights. These insights support the Data Analytics and Science Team in forming strategies and answering stakeholders.

**Data import:** CSV files are read and validated field-by-field before being stored. I used Neon for the database (local PostgreSQL or any other cloud Postgres would work). The import is designed to: (1) **Validate per row** — each row is turned into a record by `row_to_activity()`; if it returns `None` (bad or missing data), the row is skipped. (2) **Insert in batches** — valid records are collected and inserted in batches of 5000 to reduce round-trips and speed up the import. (3) **Ignore duplicates** — inserts use PostgreSQL `ON CONFLICT (event_id) DO NOTHING`, so re-runs do not fail on existing rows. (4) **Flush remaining rows** — the last partial batch is inserted the same way. The result is a bulk import that skips bad rows and is safe to re-run.

**Analytics endpoints:** (1) **Top merchant** — filter to successful events, group by merchant, sum amount, take the single merchant with highest total; return `merchant_id` and `total_volume` (2 dp). (2) **Monthly active merchants** — truncate `event_timestamp` to month, keep successful events with non-null timestamp, count distinct merchants per month, return a map of month (e.g. `"2024-01"`) to count. (3) **Product adoption** — count distinct merchants per product (all statuses), order by count descending. (4) **KYC funnel** — count distinct merchants at each of three stages (DOCUMENT_SUBMITTED, VERIFICATION_COMPLETED, TIER_UPGRADE) for successful KYC events only; return the three counts. (5) **Failure rates** — per product, failure rate = 100 × FAILED / (SUCCESS + FAILED), excluding PENDING; use conditional aggregation and `nullif` to avoid division by zero; order by rate descending; return product and rate (1 dp).

---

## Assumptions

- CSV files live in the `data/` directory with names `activities_YYYYMMDD.csv`.
- **Malformed rows:** Rows with invalid `event_id` (non-UUID), missing required fields (`merchant_id`, `product`, `event_type`, `status`), or invalid `amount` are **skipped** during import; no row is updated in place.
- **Empty `event_timestamp`** is stored as NULL; analytics that depend on time (e.g. monthly active merchants) exclude these rows.
- **Formatting:** Monetary values in responses use 2 decimal places; failure rates use 1 decimal place.
- The API is served on **port 8080** as specified.
- **psycopg2-binary** is used instead of psycopg2 to avoid configuring system-level database libraries and to meet the challenge timeline.

---

## Tech stack

- Python (FastAPI)
- PostgreSQL
- SQLAlchemy
- UV (package and env management)

---

## Setup instructions (for reviewers)

### Prerequisites

- [UV](https://docs.astral.sh/uv/) — install: `curl -LsSf https://astral.sh/uv/install.sh | sh` or `pip install uv`
- Python 3.10+
- PostgreSQL (local or cloud, e.g. Neon)
- CSV data in `data/activities_YYYYMMDD.csv`

### 1. Clone repository

```bash
git clone https://github.com/TolaniSilas/moniepoint-dreamdevs-analytics-api.git
cd moniepoint-dreamdevs-analytics-api
```

### 2. Install dependencies

```bash
uv sync
```

This creates a `.venv` and installs dependencies from `pyproject.toml`. To pin Python: `uv sync --python 3.11`.

### 3. Create PostgreSQL database

Create a database (e.g. `moniepoint_analytics`) and ensure your user has a password set.

**Local example:**

```bash
createdb moniepoint_analytics
# If needed: set password for your user (e.g. postgres) in psql
```

**Neon / cloud:** Create a project and database in the provider dashboard and copy the connection string.

### 4. Configure environment

Create a `.env` file in the **project root** (same folder as `pyproject.toml`):

```bash
cp .env.example .env
```

Edit `.env` and set `DATABASE_URL` to your database:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE_NAME
```

If the password contains special characters (e.g. `$`), use URL encoding in the value (e.g. `%24` for `$`). See [docs/DATABASE_SETUP.md](docs/DATABASE_SETUP.md) for more detail.

### 5. Import CSV data

From the project root, with CSV files in `data/`:

```bash
uv run python -m src.scripts.import_activities
```

This creates the `merchant_activities` table and loads all `data/activities_*.csv` files. Malformed rows are skipped; duplicate `event_id`s on re-run are ignored.

### 6. Start the API

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080
```

The API is available at **http://localhost:8080**. Optional: [docs/RUN_API.md](docs/RUN_API.md) for a step-by-step run and test guide.

### 7. Test endpoints

```bash
curl http://localhost:8080/
curl http://localhost:8080/analytics/top-merchant
curl http://localhost:8080/analytics/monthly-active-merchants
curl http://localhost:8080/analytics/product-adoption
curl http://localhost:8080/analytics/kyc-funnel
curl http://localhost:8080/analytics/failure-rates
```

Or open **http://localhost:8080/docs** to call the endpoints from the browser.

---

## API endpoints (port 8080)

| Endpoint | Description |
|----------|-------------|
| `GET /analytics/top-merchant` | Merchant with highest total successful transaction volume |
| `GET /analytics/monthly-active-merchants` | Unique merchants with ≥1 successful event per month |
| `GET /analytics/product-adoption` | Unique merchant count per product (sorted by count descending) |
| `GET /analytics/kyc-funnel` | KYC funnel: documents submitted, verifications completed, tier upgrades |
| `GET /analytics/failure-rates` | Failure rate per product: 100×FAILED/(SUCCESS+FAILED), PENDING excluded |

All responses are JSON.

---

## Repository structure

```
moniepoint-dreamdevs-analytics-api/
├── src/
│   ├── main.py                 # FastAPI app entrypoint
│   ├── core/                   # Config and dependencies
│   │   ├── config.py           # Settings (DATABASE_URL, data dir)
│   │   └── deps.py             # get_db
│   ├── db/base.py              # Engine, SessionLocal, Base
│   ├── models/activity.py     # Activity (merchant_activities)
│   ├── schemas/analytics.py    # Pydantic response schemas
│   ├── services/analytics.py   # AnalyticsService (queries)
│   ├── api/v1/                 # Routes
│   │   ├── router.py
│   │   └── endpoints/analytics.py
│   └── scripts/import_activities.py
├── data/                       # activities_YYYYMMDD.csv
├── docs/                       # DATABASE_SETUP, INSTALL, RUN_API
├── pyproject.toml              # Dependencies (UV)
├── .env.example                # Template for .env
└── README.md
```
