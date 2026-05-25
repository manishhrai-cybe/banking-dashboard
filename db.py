from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
import psycopg2
from psycopg2 import pool
import pandas as pd

DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "dbname":   os.getenv("DB_NAME",     "banking_db"),
    "user":     os.getenv("DB_USER",     "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres123"),
}

@st.cache_resource
def get_pool():
    return psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=5,
        **DB_CONFIG,
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