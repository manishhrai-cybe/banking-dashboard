"""
app.py — Banking Transaction Analysis Dashboard (Premium UI)
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

# ── premium CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.block-container {
    padding: 1.5rem 2.5rem 3rem 2.5rem;
    max-width: 1400px;
}

/* Header */
.dash-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(55,138,221,0.2);
    position: relative;
    overflow: hidden;
}
.dash-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(55,138,221,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.dash-title {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.5px;
}
.dash-subtitle {
    color: rgba(255,255,255,0.5);
    font-size: 0.85rem;
    margin-top: 6px;
    letter-spacing: 0.05em;
}
.dash-badge {
    display: inline-block;
    background: rgba(55,138,221,0.2);
    color: #60a5fa;
    border: 1px solid rgba(55,138,221,0.3);
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 500;
    margin-right: 6px;
    margin-top: 10px;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #1a2744, #0f172a);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    transition: transform 0.2s, border-color 0.2s;
    height: 100%;
}
.kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(55,138,221,0.4);
}
.kpi-icon {
    font-size: 1.6rem;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 2.2rem;
    font-weight: 700;
    color: #f1f5f9;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-label {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.4);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 500;
}
.kpi-card.danger {
    background: linear-gradient(145deg, #2d1515, #1a0f0f);
    border-color: rgba(239,68,68,0.3);
}
.kpi-card.danger .kpi-value { color: #f87171; }

/* Section headers */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 1.5rem 0 1rem 0;
}
.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin: 0;
}
.section-line {
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.06);
}

/* Alert cards */
.alert-card {
    background: linear-gradient(135deg, #1e1010, #2d1515);
    border: 1px solid rgba(239,68,68,0.25);
    border-left: 3px solid #ef4444;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 8px;
}
.alert-card.medium {
    background: linear-gradient(135deg, #1e1505, #2d1e08);
    border-color: rgba(245,158,11,0.25);
    border-left-color: #f59e0b;
}
.alert-name { font-size: 14px; font-weight: 600; color: #f1f5f9; }
.alert-rule { font-size: 11px; color: #94a3b8; margin-top: 2px; }
.alert-meta { font-size: 12px; color: #64748b; margin-top: 4px; }
.risk-badge-high {
    background: rgba(239,68,68,0.15);
    color: #f87171;
    border: 1px solid rgba(239,68,68,0.3);
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}
.risk-badge-med {
    background: rgba(245,158,11,0.15);
    color: #fbbf24;
    border: 1px solid rgba(245,158,11,0.3);
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

/* Segment badges */
.seg-platinum { background: linear-gradient(135deg,#1e3a5f,#1a2744); border:1px solid rgba(96,165,250,0.4); color:#93c5fd; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.seg-gold     { background: linear-gradient(135deg,#1e3a1e,#0f2210); border:1px solid rgba(74,222,128,0.4); color:#86efac; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.seg-silver   { background: linear-gradient(135deg,#1e2030,#151820); border:1px solid rgba(148,163,184,0.3); color:#94a3b8; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }
.seg-standard { background: linear-gradient(135deg,#1e1a10,#150f08); border:1px solid rgba(251,191,36,0.3); color:#fbbf24; padding:3px 10px; border-radius:20px; font-size:11px; font-weight:600; }

/* Loan card */
.loan-card {
    background: linear-gradient(145deg, #111827, #1a2744);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 10px;
}
.loan-name { font-size: 15px; font-weight: 600; color: #e2e8f0; }
.loan-meta { font-size: 12px; color: #64748b; margin-top: 2px; }

/* Progress bar */
.prog-bg {
    background: rgba(255,255,255,0.06);
    border-radius: 6px;
    height: 8px;
    margin-top: 12px;
    overflow: hidden;
}
.prog-fill {
    height: 100%;
    border-radius: 6px;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    transition: width 0.5s ease;
}

/* Stat pill */
.stat-pill {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 8px 12px;
    text-align: center;
}
.stat-pill-val { font-size: 18px; font-weight: 600; color: #f1f5f9; }
.stat-pill-lbl { font-size: 10px; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; }

/* Chart container */
.chart-wrap {
    background: linear-gradient(145deg, #111827, #0f172a);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1rem;
}

/* Skill chip */
.skill-chip {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 8px;
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.skill-name { font-size: 12px; font-weight: 500; color: #e2e8f0; }
.skill-desc { font-size: 11px; color: #64748b; }

/* Divider */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    margin: 1.5rem 0;
}

/* Resume box */
.resume-box {
    background: linear-gradient(135deg, #0f172a, #1e3a5f);
    border: 1px solid rgba(55,138,221,0.2);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-top: 1.5rem;
}
.resume-label {
    font-size: 10px;
    font-weight: 600;
    color: #60a5fa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}
.resume-text {
    font-size: 13px;
    color: #cbd5e1;
    line-height: 1.7;
}

[data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── CHART THEME ───────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#94a3b8', size=11),
    margin=dict(t=20, b=20, l=10, r=10),
    showlegend=False,
)
COLORS = ['#3b82f6','#8b5cf6','#10b981','#f59e0b','#ef4444','#64748b']

# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="dash-header">
  <p class="dash-title">🏦 Banking Transaction Analysis</p>
  <p class="dash-subtitle">REAL-TIME FRAUD DETECTION · CUSTOMER ANALYTICS · LOAN TRACKING</p>
  <div>
    <span class="dash-badge">PostgreSQL</span>
    <span class="dash-badge">Streamlit</span>
    <span class="dash-badge">Fraud Detection</span>
    <span class="dash-badge">ACID Transactions</span>
    <span class="dash-badge">Recursive CTE</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# KPI ROW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><p class="section-title">📊 Overview</p><div class="section-line"></div></div>', unsafe_allow_html=True)

try:
    kpi = queries.get_kpis().iloc[0]
    c1,c2,c3,c4,c5 = st.columns(5)
    cards = [
        (c1, "👥", int(kpi["customers"]),     "Customers",    False),
        (c2, "💳", int(kpi["accounts"]),      "Accounts",     False),
        (c3, "🔄", int(kpi["transactions"]),  "Transactions", False),
        (c4, "💰", int(kpi["active_loans"]),  "Active Loans", False),
        (c5, "🚨", int(kpi["fraud_alerts"]),  "Fraud Alerts", True),
    ]
    for col, icon, val, label, danger in cards:
        cls = "kpi-card danger" if danger else "kpi-card"
        col.markdown(f"""
        <div class="{cls}">
          <div class="kpi-icon">{icon}</div>
          <div class="kpi-value">{val}</div>
          <div class="kpi-label">{label}</div>
        </div>""", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Could not load KPIs: {e}")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CHARTS ROW
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><p class="section-title">📈 Transaction Analytics</p><div class="section-line"></div></div>', unsafe_allow_html=True)

col_l, col_r = st.columns(2)

with col_l:
    st.markdown("**Volume by channel**")
    try:
        ch = queries.get_channel_distribution()
        fig = go.Figure(go.Pie(
            labels=ch["channel"],
            values=ch["txn_count"],
            hole=0.65,
            marker=dict(colors=COLORS, line=dict(color='#0f172a', width=2)),
            textinfo='label+percent',
            textfont=dict(size=11, color='#94a3b8'),
            hovertemplate='%{label}<br>%{value} txns<extra></extra>',
        ))
        fig.update_layout(**CHART_LAYOUT, height=240)
        fig.add_annotation(text="Channel<br>Split", x=0.5, y=0.5,
            font=dict(size=12, color='#64748b'), showarrow=False)
        st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.warning(f"Chart unavailable: {e}")

with col_r:
    st.markdown("**Customer balance (₹)**")
    try:
        bal = queries.get_customer_balances()
        # Short names
        bal["short"] = bal["full_name"].apply(lambda x: x.split()[0])
        fig2 = go.Figure(go.Bar(
            x=bal["short"],
            y=bal["total_balance"],
            marker=dict(
                color=bal["total_balance"],
                colorscale=[[0,'#1e3a5f'],[0.5,'#3b82f6'],[1,'#60a5fa']],
                line=dict(width=0),
            ),
            hovertemplate='%{x}<br>₹%{y:,.0f}<extra></extra>',
        ))
        fig2.update_layout(**CHART_LAYOUT, height=240,
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickformat='₹,.0f'),
        )
        st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.warning(f"Chart unavailable: {e}")

# Daily trend
try:
    daily = queries.get_daily_kpis()
    if not daily.empty:
        st.markdown("**Daily transaction volume — last 14 days**")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=daily["txn_date"], y=daily["total_volume"],
            name="Volume", line=dict(color='#3b82f6', width=2.5),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.06)',
            hovertemplate='%{x}<br>₹%{y:,.0f}<extra></extra>',
        ))
        fig3.add_trace(go.Bar(
            x=daily["txn_date"], y=daily["flagged"],
            name="Flagged", marker_color='rgba(239,68,68,0.6)',
            yaxis='y2',
            hovertemplate='%{x}<br>%{y} flagged<extra></extra>',
        ))
        fig3.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#94a3b8', size=11),
            margin=dict(t=20, b=20, l=10, r=10),
            height=200,
            showlegend=True,
            legend=dict(orientation='h', y=1.15, font=dict(size=10)),
            xaxis=dict(gridcolor='rgba(255,255,255,0.03)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.03)', tickformat='₹,.0f'),
            yaxis2=dict(overlaying='y', side='right', showgrid=False, title='Flagged'),
            hovermode='x unified',
        )
        st.plotly_chart(fig3, use_container_width=True)
except Exception as e:
    st.warning(f"Trend unavailable: {e}")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# FRAUD ALERTS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><p class="section-title">🚨 Active Fraud Alerts</p><div class="section-line"></div></div>', unsafe_allow_html=True)

try:
    alerts = queries.get_fraud_alerts()
    if alerts.empty:
        st.success("✅ No active fraud alerts — all clear!")
    else:
        for _, row in alerts.iterrows():
            risk = float(row['risk_score'])
            cls = "alert-card" if risk >= 90 else "alert-card medium"
            badge = f'<span class="risk-badge-high">⚠ {risk}</span>' if risk >= 90 else f'<span class="risk-badge-med">⚡ {risk}</span>'
            raised = pd.to_datetime(row['raised_at']).strftime('%d %b %H:%M')
            st.markdown(f"""
            <div class="{cls}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div class="alert-name">👤 {row['full_name']} &nbsp;·&nbsp; ACC{str(row['account_id']).zfill(3)}</div>
                  <div class="alert-rule">🔴 {row['rule_triggered']}</div>
                  <div class="alert-meta">₹{float(row['amount']):,.0f} &nbsp;·&nbsp; 📍 {row['location']} &nbsp;·&nbsp; 🕐 {raised}</div>
                </div>
                <div style="text-align:right">{badge}<br><span style="font-size:10px;color:#64748b">risk score</span></div>
              </div>
            </div>""", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Fraud data unavailable: {e}")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CUSTOMER SEGMENTS
# ══════════════════════════════════════════════════════════════════════════════
col_seg, col_chart = st.columns([1, 2])

with col_seg:
    st.markdown('<div class="section-header"><p class="section-title">👥 Segments</p><div class="section-line"></div></div>', unsafe_allow_html=True)
    try:
        segs = queries.get_segments()
        seg_map = {
            'Platinum': ('seg-platinum', '💎'),
            'Gold':     ('seg-gold',     '🥇'),
            'Silver':   ('seg-silver',   '🥈'),
            'Standard': ('seg-standard', '🏷'),
        }
        for _, row in segs.iterrows():
            cls, icon = seg_map.get(row['segment'], ('seg-standard','•'))
            st.markdown(f"""
            <div style="display:flex;align-items:center;justify-content:space-between;
                        padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05)">
              <div>
                <span style="font-size:13px;font-weight:500;color:#e2e8f0">{icon} {row['full_name']}</span><br>
                <span style="font-size:11px;color:#64748b">₹{float(row['total_balance']):,.0f}</span>
              </div>
              <span class="{cls}">{row['segment']}</span>
            </div>""", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Segment data unavailable: {e}")

with col_chart:
    st.markdown('<div class="section-header"><p class="section-title">📊 Balance vs Credit Score</p><div class="section-line"></div></div>', unsafe_allow_html=True)
    try:
        segs = queries.get_segments()
        color_map = {'Platinum':'#60a5fa','Gold':'#4ade80','Silver':'#94a3b8','Standard':'#fbbf24'}
        fig4 = px.scatter(
            segs, x='credit_score', y='total_balance',
            color='segment', text='full_name',
            color_discrete_map=color_map,
            labels={'credit_score':'Credit Score','total_balance':'Balance (₹)','segment':'Segment'},
        )
        fig4.update_traces(textposition='top center', marker_size=12,
                           textfont=dict(size=10, color='#94a3b8'))
        fig4.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Inter', color='#94a3b8', size=11),
            margin=dict(t=20, b=20, l=10, r=10),
            height=300,
            showlegend=True,
            legend=dict(orientation='h', y=1.1, font=dict(size=10)),
            xaxis=dict(gridcolor='rgba(255,255,255,0.04)', title='Credit Score'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.04)', tickformat='₹,.0f', title='Balance'),
        )
        st.plotly_chart(fig4, use_container_width=True)
    except Exception as e:
        st.warning(f"Chart unavailable: {e}")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LOAN TRACKER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><p class="section-title">💳 Loan Repayment Tracker</p><div class="section-line"></div></div>', unsafe_allow_html=True)

try:
    loans = queries.get_loan_summary()
    for _, row in loans.iterrows():
        progress = float(row['paid_emis']) / float(row['total_emis']) if row['total_emis'] else 0
        pct = int(progress * 100)
        c1, c2, c3, c4 = st.columns([3,1,1,1])
        with c1:
            st.markdown(f"""
            <div class="loan-card">
              <div class="loan-name">{'🏠' if row['tenure_months'] > 60 else '💼'} {row['full_name']}</div>
              <div class="loan-meta">₹{float(row['principal']):,.0f} &nbsp;·&nbsp; {row['interest_rate']}% p.a. &nbsp;·&nbsp; {row['tenure_months']} months</div>
              <div class="prog-bg"><div class="prog-fill" style="width:{max(pct,2)}%"></div></div>
              <div style="font-size:11px;color:#64748b;margin-top:6px">{pct}% complete &nbsp;·&nbsp; ₹{float(row['total_paid']):,.0f} paid</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class="stat-pill" style="margin-top:8px">
              <div class="stat-pill-val" style="color:#4ade80">{int(row['paid_emis'])}</div>
              <div class="stat-pill-lbl">Paid</div></div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class="stat-pill" style="margin-top:8px">
              <div class="stat-pill-val" style="color:#f87171">{int(row['overdue_emis'])}</div>
              <div class="stat-pill-lbl">Overdue</div></div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class="stat-pill" style="margin-top:8px">
              <div class="stat-pill-val" style="color:#fbbf24">{int(row['pending_emis'])}</div>
              <div class="stat-pill-lbl">Pending</div></div>""", unsafe_allow_html=True)
except Exception as e:
    st.warning(f"Loan data unavailable: {e}")

# Overdue table
try:
    overdue = queries.get_overdue_emis()
    if not overdue.empty:
        st.markdown("**⚠️ Overdue EMI penalty ledger**")
        overdue["emi_amount"] = overdue["emi_amount"].apply(lambda x: f"₹{float(x):,.0f}")
        overdue["penalty"]    = overdue["penalty"].apply(lambda x: f"₹{float(x):,.0f}")
        overdue["total_due"]  = overdue["total_due"].apply(lambda x: f"₹{float(x):,.0f}")
        st.dataframe(overdue.rename(columns={
            "emi_id":"EMI","full_name":"Customer","due_date":"Due Date",
            "emi_amount":"EMI Amount","days_overdue":"Days Overdue",
            "penalty":"Penalty (2%/m)","total_due":"Total Due",
        }), use_container_width=True, hide_index=True)
except Exception as e:
    st.warning(f"Overdue data unavailable: {e}")

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SQL SKILLS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-header"><p class="section-title">⚡ SQL Skills Demonstrated</p><div class="section-line"></div></div>', unsafe_allow_html=True)

skills = [
    ("🔁", "Recursive CTE",      "Full amortisation schedule generator"),
    ("📊", "Window Functions",   "Running balance, RANK, pct share"),
    ("🔒", "ACID Transactions",  "Savepoints, FOR UPDATE row locks"),
    ("🚨", "Fraud Detection",    "Self-joins, velocity, geo-anomaly"),
    ("👁", "Analytical Views",   "3 reusable reporting views"),
    ("⚡", "Partial Indexes",    "Composite + partial for fast queries"),
]
cols = st.columns(3)
for i, (icon, name, desc) in enumerate(skills):
    with cols[i % 3]:
        st.markdown(f"""
        <div class="skill-chip" style="margin-bottom:8px">
          <span style="font-size:20px">{icon}</span>
          <div>
            <div class="skill-name">{name}</div>
            <div class="skill-desc">{desc}</div>
          </div>
        </div>""", unsafe_allow_html=True)

# ── Resume box ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="resume-box">
  <div class="resume-label">📄 Resume Line</div>
  <div class="resume-text">
    Designed a banking transaction analysis system with real-time fraud detection
    (velocity check, geo-anomaly, smurfing detection, frozen account bypass),
    recursive EMI amortisation, ACID-compliant fund transfers with savepoints,
    and customer wealth segmentation using advanced PostgreSQL —
    CTEs, window functions, self-joins, and partial indexes.
    Deployed as a live interactive dashboard using Streamlit and Plotly.
  </div>
</div>
""", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:2rem 0 1rem;color:#334155;font-size:12px">
  Built by <strong style="color:#60a5fa">Manish Rai</strong> &nbsp;·&nbsp;
  PostgreSQL + Streamlit + Plotly &nbsp;·&nbsp;
  <a href="https://github.com/manishhrai-cybe/banking-dashboard" style="color:#60a5fa;text-decoration:none">GitHub ↗</a>
</div>
""", unsafe_allow_html=True)
