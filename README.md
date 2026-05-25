# Banking Dashboard — Setup Guide

## 1. Prerequisites
- Python 3.10+
- PostgreSQL 14+ with the banking schema loaded (run `banking_analysis.sql` first)

## 2. Install dependencies
```bash
pip install -r requirements.txt
```

## 3. Set environment variables
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=banking_db
export DB_USER=postgres
export DB_PASSWORD=yourpassword
```

On Windows (PowerShell):
```powershell
$env:DB_HOST="localhost"
$env:DB_PORT="5432"
$env:DB_NAME="banking_db"
$env:DB_USER="postgres"
$env:DB_PASSWORD="yourpassword"
```

## 4. Load the schema + seed data
```bash
psql -U postgres -d banking_db -f banking_analysis.sql
```

## 5. Run the dashboard
```bash
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Project structure
```
banking_dashboard/
├── app.py          ← Streamlit UI (KPIs, charts, fraud alerts, loans)
├── queries.py      ← All SQL functions, each returning a DataFrame
├── db.py           ← Connection pool (psycopg2, cached across sessions)
├── requirements.txt
└── README.md
```

## Customisation tips
- **Add a new chart**: add a function in `queries.py`, call it in `app.py`
- **Change the DB**: only `db.py` needs editing — queries and UI are decoupled
- **Deploy to Streamlit Cloud**: add a `.streamlit/secrets.toml` and replace
  `os.getenv(...)` calls in `db.py` with `st.secrets[...]`
- **Auto-refresh**: toggle the sidebar switch — it re-runs the app every 30 s
