"""
queries.py — All SQL queries for the banking dashboard.
Each function returns a pandas DataFrame via db.run_query().
"""

from db import run_query


# ── overview KPIs ─────────────────────────────────────────────────────────────
def get_kpis():
    return run_query("""
        SELECT
            (SELECT COUNT(*) FROM customers)                          AS customers,
            (SELECT COUNT(*) FROM accounts WHERE status = 'active')   AS accounts,
            (SELECT COUNT(*) FROM transactions WHERE status != 'failed') AS transactions,
            (SELECT COUNT(*) FROM loans WHERE status = 'active')      AS active_loans,
            (SELECT COUNT(*) FROM fraud_alerts WHERE investigated = FALSE) AS fraud_alerts
    """)


# ── transaction volume by channel ─────────────────────────────────────────────
def get_channel_distribution():
    return run_query("""
        SELECT
            channel,
            COUNT(*)        AS txn_count,
            SUM(amount)     AS total_value,
            ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
        FROM transactions
        WHERE status != 'failed'
        GROUP BY channel
        ORDER BY txn_count DESC
    """)


# ── customer balance bar chart ────────────────────────────────────────────────
def get_customer_balances():
    return run_query("""
        SELECT
            c.full_name,
            COALESCE(SUM(a.balance), 0) AS total_balance
        FROM customers c
        LEFT JOIN accounts a ON a.customer_id = c.customer_id
            AND a.status = 'active'
        GROUP BY c.customer_id, c.full_name
        ORDER BY total_balance DESC
    """)


# ── active fraud alerts ───────────────────────────────────────────────────────
def get_fraud_alerts():
    return run_query("""
        SELECT
            fa.alert_id,
            c.full_name,
            fa.account_id,
            fa.rule_triggered,
            fa.risk_score,
            t.amount,
            t.channel,
            t.location,
            t.txn_time,
            fa.raised_at
        FROM fraud_alerts fa
        JOIN accounts   a  ON a.account_id  = fa.account_id
        JOIN customers  c  ON c.customer_id = a.customer_id
        JOIN transactions t ON t.txn_id     = fa.txn_id
        WHERE fa.investigated = FALSE
        ORDER BY fa.risk_score DESC
    """)


# ── customer wealth segments ──────────────────────────────────────────────────
def get_segments():
    return run_query("""
        WITH wealth AS (
            SELECT
                c.customer_id,
                c.full_name,
                c.city,
                c.credit_score,
                COALESCE(SUM(a.balance), 0) AS total_balance
            FROM customers c
            LEFT JOIN accounts a ON a.customer_id = c.customer_id
                AND a.status = 'active'
            GROUP BY c.customer_id, c.full_name, c.city, c.credit_score
        )
        SELECT *,
            CASE
                WHEN total_balance >= 500000 THEN 'Platinum'
                WHEN total_balance >= 200000 THEN 'Gold'
                WHEN total_balance >= 50000  THEN 'Silver'
                ELSE                              'Standard'
            END AS segment,
            RANK() OVER (ORDER BY total_balance DESC) AS rank
        FROM wealth
        ORDER BY total_balance DESC
    """)


# ── loan repayment tracker ────────────────────────────────────────────────────
def get_loan_summary():
    return run_query("""
        SELECT
            l.loan_id,
            c.full_name,
            l.principal,
            l.interest_rate,
            l.tenure_months,
            COUNT(e.emi_id)                                             AS total_emis,
            SUM(CASE WHEN e.status='paid'    THEN 1 ELSE 0 END)        AS paid_emis,
            SUM(CASE WHEN e.status='overdue' THEN 1 ELSE 0 END)        AS overdue_emis,
            SUM(CASE WHEN e.status='pending' THEN 1 ELSE 0 END)        AS pending_emis,
            COALESCE(SUM(e.paid_amount), 0)                            AS total_paid,
            l.status                                                    AS loan_status
        FROM loans l
        JOIN customers c ON c.customer_id = l.customer_id
        LEFT JOIN emi_schedule e ON e.loan_id = l.loan_id
        GROUP BY l.loan_id, c.full_name, l.principal,
                 l.interest_rate, l.tenure_months, l.status
        ORDER BY l.loan_id
    """)


# ── overdue EMIs ──────────────────────────────────────────────────────────────
def get_overdue_emis():
    return run_query("""
        SELECT
            e.emi_id,
            c.full_name,
            e.due_date,
            e.emi_amount,
            CURRENT_DATE - e.due_date                               AS days_overdue,
            ROUND(e.emi_amount * 0.02
                * CEIL((CURRENT_DATE - e.due_date) / 30.0), 2)     AS penalty,
            e.emi_amount
                + ROUND(e.emi_amount * 0.02
                    * CEIL((CURRENT_DATE - e.due_date) / 30.0), 2) AS total_due
        FROM emi_schedule e
        JOIN loans     l ON l.loan_id     = e.loan_id
        JOIN customers c ON c.customer_id = l.customer_id
        WHERE e.status = 'overdue'
        ORDER BY days_overdue DESC
    """)


# ── daily transaction KPIs (last 14 days) ────────────────────────────────────
def get_daily_kpis():
    return run_query("""
        SELECT
            txn_time::DATE           AS txn_date,
            COUNT(*)                 AS total_txns,
            ROUND(SUM(amount), 2)    AS total_volume,
            COUNT(*) FILTER (WHERE status='flagged') AS flagged,
            COUNT(*) FILTER (WHERE status='failed')  AS failed
        FROM transactions
        WHERE txn_time >= NOW() - INTERVAL '14 days'
        GROUP BY txn_date
        ORDER BY txn_date
    """)
