import os
import streamlit as st
import psycopg2
from psycopg2 import pool
import pandas as pd

# Works both locally (.env) and on Streamlit Cloud (st.secrets)
def get_db_config():
    try:
        return {
            "host":     st.secrets["DB_HOST"],
            "port":     int(st.secrets["DB_PORT"]),
            "dbname":   st.secrets["DB_NAME"],
            "user":     st.secrets["DB_USER"],
            "password": st.secrets["DB_PASSWORD"],
        }
    except Exception:
        return {
            "host":     os.getenv("DB_HOST",     "localhost"),
            "port":     int(os.getenv("DB_PORT", "5432")),
            "dbname":   os.getenv("DB_NAME",     "banking_db"),
            "user":     os.getenv("DB_USER",     "postgres"),
            "password": os.getenv("DB_PASSWORD", "Banking@123"),
        }

@st.cache_resource
def get_pool():
    return psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        **get_db_config(),
    )

def run_query(sql: str, params=None) -> pd.DataFrame:
    _pool = get_pool()
    conn = _pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            cols = [desc[0] for desc in cur.description]
            rows = cur.fetchall()
        return pd.DataFrame(rows, columns=cols)
    finally:
        _pool.putconn(conn)
