# Database setup

When **local PostgreSQL is working** (installed, running, and you have a user and database), the app only needs a connection URL in the environment.

---

## 1. Create `.env` in the project root

In the folder that contains `pyproject.toml` and `src/`, create a file named **`.env`**.

---

## 2. Set `DATABASE_URL` in `.env`

Add one line (replace with your own user, password, and database name):

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/moniepoint_analytics
```

- **Format:** `postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME`
- No spaces around `=`.
- If the password contains `$`, use `%24` in the URL (e.g. `mypass%24`).

---

## 3. Run the import

From the project root:

```bash
uv run python -m src.scripts.import_activities
```

Then start the API as in the main README or docs/RUN_API.md. The app reads `DATABASE_URL` from `.env` and connects to your local or cloud PostgreSQL.
