-- ============================================================
--   BANKING TRANSACTION ANALYSIS SYSTEM
--   Domain  : Banking & Finance
--   Features: Fraud Detection · Transaction Monitoring
--             Customer Analytics · Loan Repayment Tracking
-- ============================================================


-- ============================================================
-- SECTION 1 – SCHEMA SETUP
-- ============================================================

CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    full_name       VARCHAR(100)        NOT NULL,
    email           VARCHAR(150) UNIQUE NOT NULL,
    phone           VARCHAR(20),
    city            VARCHAR(60),
    credit_score    INT  CHECK (credit_score BETWEEN 300 AND 900),
    kyc_verified    BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE accounts (
    account_id      SERIAL PRIMARY KEY,
    customer_id     INT  REFERENCES customers(customer_id),
    account_type    VARCHAR(20) CHECK (account_type IN ('savings','current','loan','fd')),
    balance         NUMERIC(15,2) DEFAULT 0.00,
    currency        CHAR(3)      DEFAULT 'INR',
    status          VARCHAR(10)  DEFAULT 'active' CHECK (status IN ('active','frozen','closed')),
    opened_at       TIMESTAMP    DEFAULT NOW()
);

CREATE TABLE transactions (
    txn_id          BIGSERIAL PRIMARY KEY,
    account_id      INT      REFERENCES accounts(account_id),
    txn_type        VARCHAR(20) CHECK (txn_type IN ('credit','debit','transfer','emi','reversal')),
    amount          NUMERIC(15,2) NOT NULL CHECK (amount > 0),
    channel         VARCHAR(20) CHECK (channel IN ('atm','netbanking','upi','branch','auto')),
    merchant        VARCHAR(100),
    location        VARCHAR(100),
    txn_time        TIMESTAMP DEFAULT NOW(),
    status          VARCHAR(15) DEFAULT 'success' CHECK (status IN ('success','failed','pending','flagged')),
    reference_id    VARCHAR(50) UNIQUE,
    notes           TEXT
);

CREATE TABLE fraud_alerts (
    alert_id        SERIAL PRIMARY KEY,
    account_id      INT  REFERENCES accounts(account_id),
    txn_id          BIGINT REFERENCES transactions(txn_id),
    rule_triggered  VARCHAR(80),
    risk_score      NUMERIC(5,2),
    investigated    BOOLEAN DEFAULT FALSE,
    raised_at       TIMESTAMP DEFAULT NOW()
);

CREATE TABLE loans (
    loan_id         SERIAL PRIMARY KEY,
    customer_id     INT  REFERENCES customers(customer_id),
    account_id      INT  REFERENCES accounts(account_id),
    principal       NUMERIC(15,2) NOT NULL,
    interest_rate   NUMERIC(5,2)  NOT NULL,   -- annual %
    tenure_months   INT           NOT NULL,
    disbursed_on    DATE,
    status          VARCHAR(15) DEFAULT 'active' CHECK (status IN ('active','closed','npa','restructured'))
);

CREATE TABLE emi_schedule (
    emi_id          SERIAL PRIMARY KEY,
    loan_id         INT  REFERENCES loans(loan_id),
    due_date        DATE NOT NULL,
    emi_amount      NUMERIC(12,2) NOT NULL,
    principal_part  NUMERIC(12,2),
    interest_part   NUMERIC(12,2),
    paid_on         DATE,
    paid_amount     NUMERIC(12,2),
    status          VARCHAR(10) DEFAULT 'pending' CHECK (status IN ('pending','paid','overdue','waived'))
);


-- ============================================================
-- SECTION 2 – SEED DATA  (realistic Indian banking scenario)
-- ============================================================

INSERT INTO customers (full_name, email, phone, city, credit_score, kyc_verified) VALUES
('Arjun Mehta',      'arjun.mehta@email.in',   '9876543210', 'Mumbai',    780, TRUE),
('Priya Sharma',     'priya.sharma@email.in',  '9812345678', 'Pune',      820, TRUE),
('Rohit Verma',      'rohit.verma@email.in',   '9900112233', 'Delhi',     640, TRUE),
('Sunita Pillai',    'sunita.pillai@email.in', '9988776655', 'Bengaluru', 710, FALSE),
('Karan Singh',      'karan.singh@email.in',   '9871234560', 'Hyderabad', 760, TRUE),
('Meera Nair',       'meera.nair@email.in',    '9823456789', 'Chennai',   850, TRUE),
('Vijay Patel',      'vijay.patel@email.in',   '9765432109', 'Ahmedabad', 590, FALSE),
('Divya Rao',        'divya.rao@email.in',     '9654321098', 'Kolkata',   730, TRUE);

INSERT INTO accounts (customer_id, account_type, balance, status) VALUES
(1,'savings', 125000.00,'active'),
(1,'current', 500000.00,'active'),
(2,'savings', 310000.00,'active'),
(3,'savings',  18500.00,'active'),
(4,'savings',  72000.00,'frozen'),
(5,'current', 945000.00,'active'),
(5,'loan',         0.00,'active'),
(6,'savings', 870000.00,'active'),
(7,'savings',   5200.00,'active'),
(8,'fd',      200000.00,'active');

INSERT INTO transactions (account_id,txn_type,amount,channel,merchant,location,txn_time,status,reference_id) VALUES
(1,'debit',  4500.00,'upi',    'Swiggy',          'Mumbai',    NOW()-INTERVAL'1 day',  'success','TXN00001'),
(1,'debit',  2200.00,'upi',    'Zomato',          'Mumbai',    NOW()-INTERVAL'1 day',  'success','TXN00002'),
(1,'credit',85000.00,'netbanking',NULL,            'Mumbai',    NOW()-INTERVAL'2 days', 'success','TXN00003'),
(2,'debit', 150000.00,'netbanking','Vendor XYZ',  'Mumbai',    NOW()-INTERVAL'3 hours','success','TXN00004'),
(3,'debit',   800.00,'atm',    NULL,               'Pune',      NOW()-INTERVAL'5 hours','success','TXN00005'),
(3,'credit', 50000.00,'auto',  'Salary',          'Pune',      NOW()-INTERVAL'1 day',  'success','TXN00006'),
(4,'debit',  17000.00,'upi',   'Unknown Merchant','Delhi',     NOW()-INTERVAL'30 mins','flagged','TXN00007'),
(5,'debit',   3500.00,'atm',   NULL,               'Bengaluru', NOW()-INTERVAL'2 days', 'success','TXN00008'),
(6,'credit', 200000.00,'netbanking',NULL,          'Hyderabad', NOW()-INTERVAL'6 hours','success','TXN00009'),
(6,'debit',  95000.00,'branch','Real Estate Co',  'Hyderabad', NOW()-INTERVAL'6 hours','success','TXN00010'),
(7,'debit', 450000.00,'netbanking','Offshore Ltd', 'Chennai',  NOW()-INTERVAL'1 hour', 'flagged','TXN00011'),
(7,'debit', 430000.00,'netbanking','Offshore Ltd', 'Singapore',NOW()-INTERVAL'55 mins','flagged','TXN00012'),
(9,'debit',   1200.00,'upi',   'Petrol Pump',     'Ahmedabad', NOW()-INTERVAL'3 days', 'success','TXN00013'),
(10,'credit', 500.00,'auto',   'Interest Payout', 'Kolkata',   NOW()-INTERVAL'1 day',  'success','TXN00014');

INSERT INTO loans (customer_id,account_id,principal,interest_rate,tenure_months,disbursed_on,status) VALUES
(5,7, 1200000.00, 10.5, 120, '2022-04-01','active'),
(3,4,  300000.00,  9.0,  48, '2023-01-15','active');

-- EMI schedule for Karan Singh (loan_id=1) — 3 installments shown
INSERT INTO emi_schedule (loan_id,due_date,emi_amount,principal_part,interest_part,paid_on,paid_amount,status) VALUES
(1,'2024-01-01',16200.00,5700.00,10500.00,'2024-01-01',16200.00,'paid'),
(1,'2024-02-01',16200.00,5750.00,10450.00,'2024-02-03',16200.00,'paid'),
(1,'2024-03-01',16200.00,5800.00,10400.00, NULL,        NULL,   'overdue'),
(2,'2024-01-15', 7400.00,5000.00, 2250.00,'2024-01-15', 7400.00,'paid'),
(2,'2024-02-15', 7400.00,5040.00, 2210.00, NULL,         NULL,  'pending');

INSERT INTO fraud_alerts (account_id,txn_id,rule_triggered,risk_score) VALUES
(4, 7,'HIGH_VALUE_FROZEN_ACCOUNT',87.5),
(7,11,'RAPID_LARGE_INTERNATIONAL', 94.2),
(7,12,'RAPID_LARGE_INTERNATIONAL', 94.2);


-- ============================================================
-- SECTION 3 – TRANSACTION QUERIES
-- ============================================================

-- 3.1  Monthly transaction summary per account
SELECT
    a.account_id,
    c.full_name,
    DATE_TRUNC('month', t.txn_time)        AS txn_month,
    COUNT(*)                                AS total_txns,
    SUM(CASE WHEN t.txn_type='credit' THEN t.amount ELSE 0 END) AS total_credits,
    SUM(CASE WHEN t.txn_type='debit'  THEN t.amount ELSE 0 END) AS total_debits,
    ROUND(AVG(t.amount),2)                  AS avg_txn_value
FROM transactions t
JOIN accounts   a ON a.account_id = t.account_id
JOIN customers  c ON c.customer_id = a.customer_id
WHERE t.status != 'failed'
GROUP BY a.account_id, c.full_name, txn_month
ORDER BY txn_month DESC, total_debits DESC;


-- 3.2  Top 5 merchants by spend (last 30 days)
SELECT
    merchant,
    COUNT(*)           AS txn_count,
    SUM(amount)        AS total_spent,
    ROUND(AVG(amount),2) AS avg_spend
FROM transactions
WHERE txn_type = 'debit'
  AND merchant  IS NOT NULL
  AND txn_time  >= NOW() - INTERVAL '30 days'
GROUP BY merchant
ORDER BY total_spent DESC
LIMIT 5;


-- 3.3  Channel-wise transaction distribution
SELECT
    channel,
    COUNT(*)                    AS txn_count,
    SUM(amount)                 AS total_value,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_share
FROM transactions
GROUP BY channel
ORDER BY txn_count DESC;


-- ============================================================
-- SECTION 4 – FRAUD DETECTION LOGIC
-- ============================================================

-- 4.1  Rule 1: High-frequency small transactions (smurfing) — > 5 txns in 1 hour
SELECT
    account_id,
    COUNT(*)     AS txn_count,
    SUM(amount)  AS total_amount,
    MIN(txn_time) AS window_start,
    MAX(txn_time) AS window_end
FROM transactions
WHERE txn_time >= NOW() - INTERVAL '1 hour'
  AND status   != 'failed'
GROUP BY account_id
HAVING COUNT(*) > 5;


-- 4.2  Rule 2: Velocity check — same account, > ₹1 lakh moved within 2 hours
WITH velocity AS (
    SELECT
        account_id,
        SUM(amount)   AS moved,
        COUNT(*)      AS ops,
        MIN(txn_time) AS first_txn,
        MAX(txn_time) AS last_txn
    FROM transactions
    WHERE txn_type IN ('debit','transfer')
      AND txn_time  >= NOW() - INTERVAL '2 hours'
    GROUP BY account_id
)
SELECT v.*, c.full_name, a.balance
FROM velocity      v
JOIN accounts  a ON a.account_id  = v.account_id
JOIN customers c ON c.customer_id = a.customer_id
WHERE v.moved > 100000;


-- 4.3  Rule 3: Geographic anomaly — same account, two locations within 30 minutes
SELECT
    t1.account_id,
    t1.txn_id    AS txn1_id,
    t1.location  AS location1,
    t1.txn_time  AS time1,
    t2.txn_id    AS txn2_id,
    t2.location  AS location2,
    t2.txn_time  AS time2,
    EXTRACT(EPOCH FROM (t2.txn_time - t1.txn_time))/60 AS minutes_apart
FROM transactions t1
JOIN transactions t2
  ON  t1.account_id = t2.account_id
  AND t1.txn_id     < t2.txn_id
  AND t1.location  != t2.location
  AND t2.txn_time BETWEEN t1.txn_time AND t1.txn_time + INTERVAL '30 minutes';


-- 4.4  Rule 4: Transaction on frozen account
SELECT
    t.txn_id,
    t.account_id,
    c.full_name,
    t.amount,
    t.txn_time,
    a.status AS account_status
FROM transactions t
JOIN accounts  a ON a.account_id  = t.account_id
JOIN customers c ON c.customer_id = a.customer_id
WHERE a.status = 'frozen'
  AND t.status = 'success';


-- 4.5  Consolidated fraud risk dashboard (all active alerts)
SELECT
    fa.alert_id,
    c.full_name,
    fa.account_id,
    fa.txn_id,
    t.amount,
    t.channel,
    t.location,
    fa.rule_triggered,
    fa.risk_score,
    fa.raised_at,
    fa.investigated
FROM fraud_alerts  fa
JOIN accounts   a  ON a.account_id  = fa.account_id
JOIN customers  c  ON c.customer_id = a.customer_id
JOIN transactions t ON t.txn_id     = fa.txn_id
WHERE fa.investigated = FALSE
ORDER BY fa.risk_score DESC;


-- ============================================================
-- SECTION 5 – RECURSIVE QUERIES
-- ============================================================

-- 5.1  Cumulative running balance per account (window function + CTE)
WITH ordered_txns AS (
    SELECT
        account_id,
        txn_id,
        txn_time,
        txn_type,
        amount,
        CASE WHEN txn_type = 'credit' THEN amount ELSE -amount END AS delta
    FROM transactions
    WHERE status = 'success'
),
running AS (
    SELECT *,
        SUM(delta) OVER (
            PARTITION BY account_id
            ORDER BY txn_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS running_balance
    FROM ordered_txns
)
SELECT r.*, c.full_name
FROM running r
JOIN accounts  a ON a.account_id  = r.account_id
JOIN customers c ON c.customer_id = a.customer_id
ORDER BY r.account_id, r.txn_time;


-- 5.2  Recursive EMI amortisation schedule generator
--      (generates month-by-month schedule for any loan using pure SQL recursion)
WITH RECURSIVE amortise AS (
    -- anchor: first EMI
    SELECT
        l.loan_id,
        1                                   AS installment_no,
        l.disbursed_on + INTERVAL '1 month' AS due_date,
        l.principal                         AS opening_balance,
        ROUND(l.principal * (l.interest_rate/1200)
            / (1 - POWER(1 + l.interest_rate/1200, -l.tenure_months)), 2) AS emi,
        ROUND(l.principal * l.interest_rate / 1200, 2)  AS interest_part,
        ROUND(
            ROUND(l.principal * (l.interest_rate/1200)
                / (1 - POWER(1 + l.interest_rate/1200, -l.tenure_months)), 2)
            - ROUND(l.principal * l.interest_rate / 1200, 2)
        , 2)                                             AS principal_part,
        ROUND(l.principal
            - (ROUND(l.principal * (l.interest_rate/1200)
                / (1 - POWER(1 + l.interest_rate/1200, -l.tenure_months)), 2)
               - ROUND(l.principal * l.interest_rate / 1200, 2))
        , 2)                                             AS closing_balance
    FROM loans l
    WHERE l.loan_id = 1

    UNION ALL

    -- recursive step
    SELECT
        a.loan_id,
        a.installment_no + 1,
        a.due_date + INTERVAL '1 month',
        a.closing_balance,
        a.emi,
        ROUND(a.closing_balance * (SELECT interest_rate/1200 FROM loans WHERE loan_id = a.loan_id), 2),
        ROUND(a.emi - ROUND(a.closing_balance * (SELECT interest_rate/1200 FROM loans WHERE loan_id = a.loan_id), 2), 2),
        ROUND(a.closing_balance
            - (a.emi - ROUND(a.closing_balance * (SELECT interest_rate/1200 FROM loans WHERE loan_id = a.loan_id), 2))
        , 2)
    FROM amortise a
    WHERE a.installment_no < (SELECT tenure_months FROM loans WHERE loan_id = a.loan_id)
      AND a.closing_balance > 0
)
SELECT
    installment_no,
    due_date,
    opening_balance,
    interest_part,
    principal_part,
    emi         AS total_emi,
    closing_balance
FROM amortise
ORDER BY installment_no;


-- ============================================================
-- SECTION 6 – CUSTOMER ACCOUNT ANALYTICS
-- ============================================================

-- 6.1  Customer 360: balance, txn count, fraud flags, loan exposure
SELECT
    c.customer_id,
    c.full_name,
    c.city,
    c.credit_score,
    COUNT(DISTINCT a.account_id)                               AS num_accounts,
    SUM(a.balance)                                             AS total_balance,
    COUNT(DISTINCT t.txn_id)                                   AS lifetime_txns,
    COALESCE(SUM(l.principal),0)                               AS total_loan_principal,
    COUNT(DISTINCT fa.alert_id)                                AS fraud_alerts
FROM customers   c
LEFT JOIN accounts    a  ON a.customer_id  = c.customer_id
LEFT JOIN transactions t  ON t.account_id  = a.account_id
LEFT JOIN loans        l  ON l.customer_id = c.customer_id
LEFT JOIN fraud_alerts fa ON fa.account_id = a.account_id
GROUP BY c.customer_id, c.full_name, c.city, c.credit_score
ORDER BY total_balance DESC;


-- 6.2  High-value customer segmentation (RANK by net worth tier)
WITH wealth AS (
    SELECT
        c.customer_id,
        c.full_name,
        SUM(a.balance) AS total_balance
    FROM customers c
    JOIN accounts  a ON a.customer_id = c.customer_id
    WHERE a.status = 'active'
    GROUP BY c.customer_id, c.full_name
)
SELECT *,
    CASE
        WHEN total_balance >= 500000 THEN 'PLATINUM'
        WHEN total_balance >= 200000 THEN 'GOLD'
        WHEN total_balance >= 50000  THEN 'SILVER'
        ELSE                              'STANDARD'
    END AS segment,
    RANK() OVER (ORDER BY total_balance DESC) AS wealth_rank
FROM wealth
ORDER BY total_balance DESC;


-- 6.3  Dormant accounts (no transaction in last 180 days)
SELECT
    a.account_id,
    c.full_name,
    a.account_type,
    a.balance,
    MAX(t.txn_time) AS last_txn_date,
    NOW()::DATE - MAX(t.txn_time)::DATE AS days_since_last_txn
FROM accounts  a
JOIN customers c ON c.customer_id = a.customer_id
LEFT JOIN transactions t ON t.account_id = a.account_id
GROUP BY a.account_id, c.full_name, a.account_type, a.balance
HAVING MAX(t.txn_time) < NOW() - INTERVAL '180 days'
    OR MAX(t.txn_time) IS NULL;


-- ============================================================
-- SECTION 7 – LOAN REPAYMENT TRACKING
-- ============================================================

-- 7.1  Current repayment status per loan
SELECT
    l.loan_id,
    c.full_name,
    l.principal,
    l.interest_rate,
    l.tenure_months,
    COUNT(e.emi_id)                                          AS total_emis,
    SUM(CASE WHEN e.status='paid'    THEN 1 ELSE 0 END)     AS paid_emis,
    SUM(CASE WHEN e.status='overdue' THEN 1 ELSE 0 END)     AS overdue_emis,
    SUM(CASE WHEN e.status='pending' THEN 1 ELSE 0 END)     AS pending_emis,
    COALESCE(SUM(e.paid_amount),0)                          AS total_paid,
    l.principal - COALESCE(SUM(e.principal_part)
        FILTER (WHERE e.status='paid'),0)                   AS outstanding_principal,
    l.status                                                 AS loan_status
FROM loans         l
JOIN customers     c ON c.customer_id = l.customer_id
LEFT JOIN emi_schedule e ON e.loan_id = l.loan_id
GROUP BY l.loan_id, c.full_name, l.principal, l.interest_rate,
         l.tenure_months, l.status;


-- 7.2  Overdue EMI report with penalty calculation (2% flat penalty per month)
SELECT
    e.emi_id,
    l.loan_id,
    c.full_name,
    e.due_date,
    e.emi_amount,
    CURRENT_DATE - e.due_date                         AS days_overdue,
    ROUND(e.emi_amount * 0.02
        * CEIL((CURRENT_DATE - e.due_date) / 30.0), 2) AS penalty_amount,
    e.emi_amount
        + ROUND(e.emi_amount * 0.02
            * CEIL((CURRENT_DATE - e.due_date) / 30.0), 2) AS total_due
FROM emi_schedule e
JOIN loans     l ON l.loan_id     = e.loan_id
JOIN customers c ON c.customer_id = l.customer_id
WHERE e.status = 'overdue'
ORDER BY days_overdue DESC;


-- 7.3  NPA (Non-Performing Asset) candidate detection
--      Loans with 3+ consecutive overdue EMIs qualify as NPA
SELECT
    l.loan_id,
    c.full_name,
    l.principal,
    COUNT(*) AS consecutive_overdue
FROM emi_schedule e
JOIN loans     l ON l.loan_id     = e.loan_id
JOIN customers c ON c.customer_id = l.customer_id
WHERE e.status = 'overdue'
GROUP BY l.loan_id, c.full_name, l.principal
HAVING COUNT(*) >= 3;


-- ============================================================
-- SECTION 8 – ACID TRANSACTION DEMOS
-- ============================================================

-- 8.1  Atomic fund transfer between accounts (ACID-compliant)
BEGIN;

    -- Step 1: Verify sender has sufficient balance
    DO $$
    DECLARE
        v_balance NUMERIC;
    BEGIN
        SELECT balance INTO v_balance FROM accounts WHERE account_id = 1 FOR UPDATE;
        IF v_balance < 10000 THEN
            RAISE EXCEPTION 'Insufficient funds: balance is %', v_balance;
        END IF;
    END $$;

    -- Step 2: Debit sender
    UPDATE accounts
    SET balance = balance - 10000
    WHERE account_id = 1;

    -- Step 3: Credit receiver
    UPDATE accounts
    SET balance = balance + 10000
    WHERE account_id = 3;

    -- Step 4: Log both legs of the transfer
    INSERT INTO transactions (account_id,txn_type,amount,channel,notes,reference_id)
    VALUES (1,'debit', 10000,'netbanking','Transfer to ACC003','TXN-XFER-001');

    INSERT INTO transactions (account_id,txn_type,amount,channel,notes,reference_id)
    VALUES (3,'credit',10000,'netbanking','Transfer from ACC001','TXN-XFER-002');

COMMIT;


-- 8.2  Savepoint demo — partial rollback during batch EMI posting
BEGIN;

    SAVEPOINT before_emi_batch;

    UPDATE emi_schedule SET status='paid', paid_on=CURRENT_DATE, paid_amount=emi_amount
    WHERE emi_id = 5 AND status = 'pending';

    -- Simulate a downstream error (e.g. ledger update failure)
    SAVEPOINT after_emi_5;

    -- Intentional error caught → rollback only the bad step
    ROLLBACK TO SAVEPOINT before_emi_batch;

    -- Retry with corrected data
    UPDATE emi_schedule SET status='paid', paid_on=CURRENT_DATE, paid_amount=emi_amount
    WHERE emi_id = 5 AND status IN ('pending','overdue');

COMMIT;


-- ============================================================
-- SECTION 9 – INDEXES & PERFORMANCE
-- ============================================================

CREATE INDEX idx_txn_account_time   ON transactions(account_id, txn_time DESC);
CREATE INDEX idx_txn_status         ON transactions(status);
CREATE INDEX idx_txn_time           ON transactions(txn_time DESC);
CREATE INDEX idx_fraud_investigated ON fraud_alerts(investigated) WHERE investigated = FALSE;
CREATE INDEX idx_emi_status         ON emi_schedule(status);
CREATE INDEX idx_accounts_customer  ON accounts(customer_id);
CREATE INDEX idx_loans_customer     ON loans(customer_id);


-- ============================================================
-- SECTION 10 – ANALYTICAL VIEWS
-- ============================================================

-- View: Real-time fraud watchlist
CREATE OR REPLACE VIEW v_fraud_watchlist AS
SELECT
    fa.alert_id,
    c.full_name,
    a.account_id,
    fa.rule_triggered,
    fa.risk_score,
    t.amount,
    t.channel,
    t.location,
    t.txn_time,
    fa.raised_at
FROM fraud_alerts  fa
JOIN accounts   a  ON a.account_id  = fa.account_id
JOIN customers  c  ON c.customer_id = a.customer_id
JOIN transactions t ON t.txn_id     = fa.txn_id
WHERE fa.investigated = FALSE
ORDER BY fa.risk_score DESC;

-- View: Daily transaction KPIs
CREATE OR REPLACE VIEW v_daily_txn_kpi AS
SELECT
    txn_time::DATE           AS txn_date,
    COUNT(*)                 AS total_txns,
    SUM(amount)              AS total_volume,
    COUNT(*) FILTER (WHERE status='flagged')  AS flagged_count,
    COUNT(*) FILTER (WHERE status='failed')   AS failed_count,
    ROUND(AVG(amount),2)     AS avg_txn_amount,
    MAX(amount)              AS max_txn_amount
FROM transactions
GROUP BY txn_date
ORDER BY txn_date DESC;

-- View: Loan health summary
CREATE OR REPLACE VIEW v_loan_health AS
SELECT
    l.loan_id,
    c.full_name,
    l.principal,
    l.status                                                        AS loan_status,
    COUNT(e.emi_id)                                                 AS total_emis,
    SUM(CASE WHEN e.status='overdue' THEN 1 ELSE 0 END)            AS overdue_count,
    ROUND(100.0 * SUM(CASE WHEN e.status='paid' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(e.emi_id),0), 1)                            AS repayment_rate_pct
FROM loans         l
JOIN customers     c ON c.customer_id = l.customer_id
LEFT JOIN emi_schedule e ON e.loan_id  = l.loan_id
GROUP BY l.loan_id, c.full_name, l.principal, l.status;
