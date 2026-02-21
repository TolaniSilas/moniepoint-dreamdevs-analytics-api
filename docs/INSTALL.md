# Manual installation guide

Follow these steps to install the project dependencies yourself.

---

## Step 1: Install UV (if you don’t have it)

UV is the tool used to create the virtual environment and install dependencies.

**Option A – Official installer (recommended)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then restart your terminal or run:

```bash
source $HOME/.local/bin/env
```

**Option B – With pip**

```bash
pip install uv
```

**Check it’s installed**

```bash
uv --version
```

You should see a version number (e.g. `uv 0.4.x`).

---

## Step 2: Go to the project folder

Open a terminal and change into the project root (where `pyproject.toml` and `src/` are):

```bash
cd /path/to/moniepoint-dreamdevs-analytics-api
```

Replace `/path/to/` with your actual path (e.g. `~/Documents/moniepoint-dreamdevs-analytics-api`).

---

## Step 3: Create the virtual environment and install dependencies

Run:

```bash
uv sync
```

This will:

1. Create a `.venv` folder in the project (if it doesn’t exist).
2. Use the Python version UV finds (or the one you set with `UV_PYTHON`).
3. Install every package listed under `dependencies` in `pyproject.toml` into `.venv`.

Wait until it finishes without errors.

---

## Step 4: Confirm installation

**Option A – Use the venv directly**

Activate the environment:

```bash
source .venv/bin/activate
```

On Windows (PowerShell):

```bash
.venv\Scripts\Activate.ps1
```

Then check that key packages are available:

```bash
python -c "import fastapi, sqlalchemy, pydantic; print('OK')"
```

You should see `OK`.

**Option B – Use UV without activating**

You can run commands without activating by prefixing with `uv run`:

```bash
uv run python -c "import fastapi; print('OK')"
```

---

## Step 5: Run the project (after DB setup)

Once PostgreSQL is set up and `.env` is configured:

**Import CSV data**

```bash
uv run python -m src.scripts.import_activities
```

**Start the API**

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8080
```

Or with the venv activated:

```bash
source .venv/bin/activate
python -m src.scripts.import_activities
uvicorn src.main:app --host 0.0.0.0 --port 8080
```

---

## Troubleshooting

| Issue | What to do |
|--------|------------|
| `uv: command not found` | Install UV (Step 1) and ensure it’s on your `PATH` (e.g. `$HOME/.local/bin`). |
| `No such file or directory` when running `uv sync` | Make sure you’re in the project root (folder that contains `pyproject.toml`). |
| Permission or network errors | Run the terminal as a normal user and check your internet connection; corporate proxies may need extra config. |

---

## Summary

1. Install **UV** (`curl ...` or `pip install uv`).
2. **`cd`** into the project directory.
3. Run **`uv sync`** to create `.venv` and install dependencies.
4. Use **`uv run ...`** or **`source .venv/bin/activate`** then **`python` / `uvicorn`** to run the app.
