# Running the API endpoints

After [importing the CSV data](README.md#5-import-csv-data) into your database (Neon was used as the database (db) for easy implementation - any db either local or on cloud could be utilized), run the API and hit the five analytics endpoints.

---

## 1. Ensure the database is reachable

- Your `.env` in the project root must contain a valid `DATABASE_URL` (e.g. your Neon connection string).
- The database must already have the `merchant_activities` table and data (from `uv run python -m src.scripts.import_activities`).

---

## 2. Start the API server

From the **project root**:

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080
```

You should see something like:

```
INFO:     Uvicorn running on http://0.0.0.0:8080
INFO:     Application startup complete.
```

Leave this terminal running. The API is now available at **http://localhost:8080**.

---

## 3. Test the endpoints

Open a **new terminal** (or use a browser/Postman). Base URL: **http://localhost:8080**.

### Health check

```bash
curl http://localhost:8080/
```

Expected: `{"service":"Moniepoint Analytics API","status":"ok"}`

### 1. Top merchant

```bash
curl http://localhost:8080/analytics/top-merchant
```

Expected shape: `{"merchant_id":"MRC-...","total_volume":12345678.90}`

### 2. Monthly active merchants

```bash
curl http://localhost:8080/analytics/monthly-active-merchants
```

Expected shape: `{"2024-01":8234,"2024-02":8456,...}`

### 3. Product adoption

```bash
curl http://localhost:8080/analytics/product-adoption
```

Expected shape: `{"POS":15234,"AIRTIME":12456,"BILLS":10234,...}`

### 4. KYC funnel

```bash
curl http://localhost:8080/analytics/kyc-funnel
```

Expected shape: `{"documents_submitted":5432,"verifications_completed":4521,"tier_upgrades":3890}`

### 5. Failure rates

```bash
curl http://localhost:8080/analytics/failure-rates
```

Expected shape: `[{"product":"BILLS","failure_rate":5.2},{"product":"AIRTIME","failure_rate":4.1},...]`

---

## 4. Optional: interactive API docs

With the server running, open in a browser:

- **Swagger UI:** http://localhost:8080/docs  
- **ReDoc:** http://localhost:8080/redoc  

You can call all five analytics endpoints from there.

---

## Quick checklist

| Step | Action |
|------|--------|
| 1 | `.env` has correct `DATABASE_URL` (Neon or local PostgreSQL) |
| 2 | Data already imported (`merchant_activities` table has rows) |
| 3 | `uv run uvicorn src.main:app --host 0.0.0.0 --port 8080` |
| 4 | Test with the `curl` commands above or use http://localhost:8080/docs |
