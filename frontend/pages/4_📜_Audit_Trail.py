"""Audit Trail — Immutable agent action log for India MSME LOS."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests
import pandas as pd
from styles import page_config_dark, sidebar_status

page_config_dark("Audit Trail", "📜")

API = st.session_state.get("api_url", "http://localhost:8000")

st.sidebar.markdown("""
<div style="padding:0.5rem 0 1rem;">
  <div style="font-size:1.3rem;font-weight:800;color:#FFFFFF;">Audit Trail</div>
  <div style="font-size:0.75rem;color:#8A8FA8;">Immutable Agent Action Log</div>
</div>
""", unsafe_allow_html=True)
sidebar_status()

# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div style="font-size:1.8rem;font-weight:800;letter-spacing:-0.03em;color:#FFFFFF;">Audit Trail</div>
  <div style="font-size:0.85rem;color:#8A8FA8;">Every agent decision, state transition, and data transformation — immutably logged.</div>
</div>
""", unsafe_allow_html=True)

# ── Filters ────────────────────────────────────────────────────
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    app_filter = st.text_input(
        "Filter by Application ID",
        placeholder="MSME3A7B2F — leave empty for all",
        label_visibility="collapsed",
        key="audit_app_filter",
    )
with col2:
    agent_filter = st.selectbox(
        "Agent", ["All", "orchestrator", "kyc", "document", "underwriting", "pricing", "sarah"],
        label_visibility="collapsed",
        key="audit_agent_filter",
    )
with col3:
    limit = st.selectbox("Show", [50, 100, 200, 500], label_visibility="collapsed", key="audit_limit")

# ── Fetch Entries ──────────────────────────────────────────────
try:
    if app_filter:
        r = requests.get(f"{API}/api/dashboard/audit/{app_filter}", timeout=3)
    else:
        r = requests.get(f"{API}/api/dashboard/audit?limit={limit}", timeout=3)

    if r.status_code == 200:
        entries = r.json()
    else:
        entries = []
except Exception:
    st.error("Cannot connect to backend.")
    entries = []

if agent_filter and agent_filter != "All":
    entries = [e for e in entries if e.get("agent") == agent_filter]

if not entries:
    st.markdown("""
    <div class="rv-card" style="text-align:center;padding:3rem;color:#8A8FA8;">
      <div style="font-size:2rem;margin-bottom:0.8rem;">📭</div>
      <div style="font-weight:600;">No audit entries found</div>
      <div style="font-size:0.85rem;margin-top:0.3rem;">Submit an application and run the pipeline to generate audit logs.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Summary Stats ─────────────────────────────────────────────
from collections import Counter
agent_counts = Counter(e["agent"] for e in entries)
action_counts = Counter(e["action"] for e in entries)

col_a, col_b, col_c = st.columns(3)
with col_a:
    st.markdown(f"""
    <div class="rv-card" style="padding:1rem 1.2rem;">
      <div class="rv-section-title">TOTAL EVENTS</div>
      <div style="font-size:1.8rem;font-weight:800;color:#FFFFFF;">{len(entries)}</div>
    </div>
    """, unsafe_allow_html=True)
with col_b:
    top_agent = agent_counts.most_common(1)[0] if agent_counts else ("—", 0)
    st.markdown(f"""
    <div class="rv-card" style="padding:1rem 1.2rem;">
      <div class="rv-section-title">MOST ACTIVE AGENT</div>
      <div style="font-size:1.8rem;font-weight:800;color:#7B6BF8;">{top_agent[0]}</div>
      <div style="font-size:0.8rem;color:#8A8FA8;">{top_agent[1]} actions</div>
    </div>
    """, unsafe_allow_html=True)
with col_c:
    top_action = action_counts.most_common(1)[0] if action_counts else ("—", 0)
    st.markdown(f"""
    <div class="rv-card" style="padding:1rem 1.2rem;">
      <div class="rv-section-title">TOP ACTION</div>
      <div style="font-size:1.1rem;font-weight:800;color:#00D48A;">{top_action[0].replace('_',' ')}</div>
      <div style="font-size:0.8rem;color:#8A8FA8;">{top_action[1]} times</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Table View ─────────────────────────────────────────────────
AGENT_ICONS = {
    "sarah": "💬", "kyc": "🛡️", "compliance": "🛡️",
    "document": "📄", "underwriting": "📊",
    "pricing": "💰", "orchestrator": "⚙️",
}
AGENT_COLORS = {
    "sarah": "#5B4CF5", "kyc": "#3B9EF5", "compliance": "#3B9EF5",
    "document": "#F5A623", "underwriting": "#00D48A",
    "pricing": "#FF3B57", "orchestrator": "#8A8FA8",
}

tab1, tab2 = st.tabs(["📋 Event Log", "📊 Table View"])

with tab1:
    for entry in entries[:100]:
        agent = entry.get("agent", "")
        action = entry.get("action", "")
        ts = entry.get("created_at", "")[:19]
        app_id_e = entry.get("application_id", "")
        details = entry.get("details", {})
        icon = AGENT_ICONS.get(agent, "❓")
        color = AGENT_COLORS.get(agent, "#8A8FA8")

        with st.expander(
            f"{icon}  {agent.upper()} — {action.replace('_', ' ')}  ·  {app_id_e}  ·  {ts}"
        ):
            col_d1, col_d2 = st.columns([1, 2])
            with col_d1:
                st.markdown(f"""
                <div class="rv-card" style="padding:0.8rem 1rem;">
                  <div class="rv-stat-row"><span class="rv-stat-label">Agent</span><span style="color:{color};font-weight:700;">{icon} {agent}</span></div>
                  <div class="rv-stat-row"><span class="rv-stat-label">Action</span><span class="rv-stat-value" style="font-size:0.82rem;">{action.replace('_',' ')}</span></div>
                  <div class="rv-stat-row"><span class="rv-stat-label">App ID</span><span style="font-family:monospace;color:#7B6BF8;font-size:0.85rem;">{app_id_e}</span></div>
                  <div class="rv-stat-row"><span class="rv-stat-label">Time</span><span class="rv-stat-value" style="font-size:0.8rem;">{ts}</span></div>
                </div>
                """, unsafe_allow_html=True)
            with col_d2:
                if details:
                    st.json(details)
                else:
                    st.markdown('<div style="color:#8A8FA8;font-size:0.85rem;">No details recorded</div>', unsafe_allow_html=True)

with tab2:
    df = pd.DataFrame(entries[:200])
    if not df.empty:
        display_cols = ["created_at", "application_id", "agent", "action"]
        df_display = df[display_cols].copy()
        df_display.columns = ["Timestamp", "Application", "Agent", "Action"]
        df_display["Timestamp"] = df_display["Timestamp"].str[:19]
        df_display["Action"] = df_display["Action"].str.replace("_", " ")
        st.dataframe(df_display, use_container_width=True, height=500)
