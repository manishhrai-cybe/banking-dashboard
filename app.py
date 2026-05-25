"""
app.py — Banking Transaction Analysis Dashboard
Run: streamlit run app.py
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import queries

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Banking Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── minimal custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    [data-testid="stMetricValue"] { font-size: 2rem !important; }
    .risk-high  { color: #A32D2D; font-weight: 600; }
    .risk-med   { color: #854F0B; font-weight: 600; }
    .seg-platinum { background:#E6F1FB; color:#0C447C; padding:2px 8px; border-radius:4px; font-size:12px; }
    .seg-gold     { background:#EAF3DE; color:#3B6D11; padding:2px 8px; border-radius:4px; font-size:12px; }
    .seg-silver   { background:#F1EFE8; color:#5F5E5A; padding:2px 8px; border-radius:4px; font-size:12px; }
    .seg-standard { background:#FAEEDA; color:#854F0B; padding:2px 8px; border-radius:4px; font-size:12px; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── colour palette (consistent across all charts) ────────────────────────────
COLORS = {
    "blue":   "#378ADD",
    "purple": "#534AB7",
    "teal":   "#1D9E75",
    "amber":  "#BA7517",
    "red":    "#E24B4A",
    "gray":   "#888780",
}
SEGMENT_COLORS = {
    "Platinum": COLORS["blue"],
    "Gold":     COLORS["teal"],
    "Silver":   COLORS["gray"],
    "Standard": COLORS["amber"],
}


# ── header ────────────────────────────────────────────────────────────────────
st.markdown("## 🏦 Banking Transaction Analysis Dashboard")
st.markdown(
    "<p style='color:#888;font-size:14px;margin-top:-12px'>"
    "PostgreSQL · Fraud Detection · ACID · Recursive CTE · Window Functions</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── auto-refresh (optional) ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    auto_refresh = st.toggle("Auto-refresh (30 s)", value=False)
    if auto_refresh:
        import time
        st.caption("Next refresh in 30 s…")
        time.sleep(30)
        st.rerun()
    st.caption("Connect to your PostgreSQL instance by setting the "
               "`DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` "
               "environment variables before running.")


# ═══════════════════════════════════════════════════════════════
# SECTION 1 — KPI OVERVIEW
# ═══════════════════════════════════════════════════════════════
st.subheader("Overview")

try:
    kpi = queries.get_kpis().iloc[0]
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Customers",       int(kpi["customers"]))
    c2.metric("Active accounts", int(kpi["accounts"]))
    c3.metric("Transactions",    int(kpi["transactions"]))
    c4.metric("Active loans",    int(kpi["active_loans"]))
    # Fraud alerts — highlighted in red if non-zero
    fraud_count = int(kpi["fraud_alerts"])
    c5.metric(
        "🚨 Fraud alerts",
        fraud_count,
        delta=f"{fraud_count} open" if fraud_count else "All clear",
        delta_color="inverse" if fraud_count else "normal",
    )
except Exception as e:
    st.error(f"Could not load KPIs: {e}")


# ═══════════════════════════════════════════════════════════════
# SECTION 2 — TRANSACTION CHARTS
# ═══════════════════════════════════════════════════════════════
st.divider()
st.subheader("Transaction analytics")

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("**Volume by channel**")
    try:
        ch = queries.get_channel_distribution()
        fig = px.pie(
            ch,
            names="channel",
            values="txn_count",
            hole=0.55,
            color="channel",
            color_discrete_map={
                "upi":        COLORS["blue"],
                "netbanking": COLORS["purple"],
                "atm":        COLORS["teal"],
                "branch":     COLORS["gray"],
                "auto":       COLORS["amber"],
            },
        )
        fig.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{value} txns")
        fig.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
        )
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Chart unavailable: {e}")

with col_right:
    st.markdown("**Customer balance (₹)**")
    try:
        bal = queries.get_customer_balances()
        fig2 = px.bar(
            bal,
            x="total_balance",
            y="full_name",
            orientation="h",
            color="total_balance",
            color_continuous_scale=["#B5D4F4", "#185FA5"],
            labels={"total_balance": "Balance (₹)", "full_name": ""},
        )
        fig2.update_coloraxes(showscale=False)
        fig2.update_traces(
            hovertemplate="₹%{x:,.0f}",
            marker_line_width=0,
        )
        fig2.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            height=260,
            yaxis=dict(categoryorder="total ascending"),
            xaxis_tickformat="₹,.0f",
        )
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.warning(f"Chart unavailable: {e}")

# Daily trend chart (full width)
try:
    daily = queries.get_daily_kpis()
    if not daily.empty:
        st.markdown("**Daily transaction volume — last 14 days**")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=daily["txn_date"], y=daily["total_volume"],
            name="Volume (₹)", line=dict(color=COLORS["blue"], width=2),
            fill="tozeroy", fillcolor="rgba(55,138,221,0.08)",
        ))
        fig3.add_trace(go.Bar(
            x=daily["txn_date"], y=daily["flagged"],
            name="Flagged", marker_color=COLORS["red"], opacity=0.7,
            yaxis="y2",
        ))
        fig3.update_layout(
            height=220,
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=1.15),
            yaxis=dict(title="Volume (₹)", tickformat="₹,.0f"),
            yaxis2=dict(title="Flagged", overlaying="y", side="right", showgrid=False),
            hovermode="x unified",
        )
        st.plotly_chart(fig3, use_container_width=True)
except Exception as e:
    st.warning(f"Trend chart unavailable: {e}")


# ═══════════════════════════════════════════════════════════════
# SECTION 3 — FRAUD ALERTS
# ═══════════════════════════════════════════════════════════════
st.divider()
st.subheader("🚨 Active fraud alerts")

try:
    alerts = queries.get_fraud_alerts()
    if alerts.empty:
        st.success("No active fraud alerts.")
    else:
        # Colour-code risk score
        def style_risk(val):
            if val >= 90:
                return "color: #A32D2D; font-weight: 600"
            elif val >= 80:
                return "color: #854F0B; font-weight: 600"
            return ""

        # Format columns for display
        display = alerts[[
            "full_name", "account_id", "rule_triggered",
            "risk_score", "amount", "location", "raised_at"
        ]].rename(columns={
            "full_name":      "Customer",
            "account_id":     "Account",
            "rule_triggered": "Rule",
            "risk_score":     "Risk",
            "amount":         "Amount (₹)",
            "location":       "Location",
            "raised_at":      "Raised at",
        })
        display["Amount (₹)"] = display["Amount (₹)"].apply(lambda x: f"₹{x:,.0f}")
        display["Raised at"]  = pd.to_datetime(display["Raised at"]).dt.strftime("%d %b %H:%M")

        st.dataframe(
            display.style.applymap(style_risk, subset=["Risk"]),
            use_container_width=True,
            hide_index=True,
        )
except Exception as e:
    st.warning(f"Fraud data unavailable: {e}")


# ═══════════════════════════════════════════════════════════════
# SECTION 4 — CUSTOMER SEGMENTS
# ═══════════════════════════════════════════════════════════════
st.divider()
st.subheader("Customer wealth segments")

try:
    segs = queries.get_segments()

    # Summary counts
    counts = segs["segment"].value_counts()
    c1, c2, c3, c4 = st.columns(4)
    for col, seg, color in [
        (c1, "Platinum", COLORS["blue"]),
        (c2, "Gold",     COLORS["teal"]),
        (c3, "Silver",   COLORS["gray"]),
        (c4, "Standard", COLORS["amber"]),
    ]:
        col.metric(seg, counts.get(seg, 0))

    # Scatter: balance vs credit score, coloured by segment
    fig4 = px.scatter(
        segs,
        x="credit_score",
        y="total_balance",
        color="segment",
        text="full_name",
        color_discrete_map=SEGMENT_COLORS,
        labels={"credit_score": "Credit score", "total_balance": "Total balance (₹)", "segment": "Segment"},
        title="Balance vs credit score",
    )
    fig4.update_traces(textposition="top center", marker_size=10)
    fig4.update_layout(
        height=320,
        margin=dict(t=40, b=20, l=20, r=20),
        yaxis_tickformat="₹,.0f",
    )
    st.plotly_chart(fig4, use_container_width=True)

    # Full table
    with st.expander("Full segment table"):
        display_segs = segs[[
            "rank", "full_name", "city", "credit_score", "total_balance", "segment"
        ]].rename(columns={
            "rank":          "#",
            "full_name":     "Customer",
            "city":          "City",
            "credit_score":  "Credit score",
            "total_balance": "Balance (₹)",
            "segment":       "Segment",
        })
        display_segs["Balance (₹)"] = display_segs["Balance (₹)"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(display_segs, use_container_width=True, hide_index=True)

except Exception as e:
    st.warning(f"Segment data unavailable: {e}")


# ═══════════════════════════════════════════════════════════════
# SECTION 5 — LOAN REPAYMENT TRACKER
# ═══════════════════════════════════════════════════════════════
st.divider()
st.subheader("Loan repayment tracker")

try:
    loans = queries.get_loan_summary()
    if loans.empty:
        st.info("No active loans.")
    else:
        for _, row in loans.iterrows():
            progress = row["paid_emis"] / row["total_emis"] if row["total_emis"] else 0
            with st.container(border=True):
                lc1, lc2, lc3, lc4, lc5 = st.columns([3, 2, 1, 1, 1])
                lc1.markdown(f"**{row['full_name']}**  \n₹{row['principal']:,.0f} · {row['interest_rate']}% p.a. · {row['tenure_months']} months")
                lc2.markdown(f"**Status:** `{row['loan_status'].upper()}`")
                lc3.metric("Paid",    int(row["paid_emis"]))
                lc4.metric("Overdue", int(row["overdue_emis"]),
                           delta=f"{int(row['overdue_emis'])} overdue" if row["overdue_emis"] else None,
                           delta_color="inverse")
                lc5.metric("Pending", int(row["pending_emis"]))
                st.progress(float(progress), text=f"{int(progress*100)}% complete — ₹{row['total_paid']:,.0f} paid")

except Exception as e:
    st.warning(f"Loan data unavailable: {e}")

# Overdue EMI penalty table
try:
    overdue = queries.get_overdue_emis()
    if not overdue.empty:
        st.markdown("**Overdue EMI penalty ledger**")
        overdue["emi_amount"]  = overdue["emi_amount"].apply(lambda x: f"₹{x:,.0f}")
        overdue["penalty"]     = overdue["penalty"].apply(lambda x: f"₹{x:,.0f}")
        overdue["total_due"]   = overdue["total_due"].apply(lambda x: f"₹{x:,.0f}")
        st.dataframe(
            overdue.rename(columns={
                "emi_id":      "EMI",
                "full_name":   "Customer",
                "due_date":    "Due date",
                "emi_amount":  "EMI amount",
                "days_overdue":"Days overdue",
                "penalty":     "Penalty (2%/m)",
                "total_due":   "Total due",
            }),
            use_container_width=True,
            hide_index=True,
        )
except Exception as e:
    st.warning(f"Overdue EMI data unavailable: {e}")


# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════
st.divider()
st.caption(
    "Banking Transaction Analysis System · PostgreSQL + Streamlit · "
    "Fraud detection · ACID transactions · Recursive CTE amortisation"
)
