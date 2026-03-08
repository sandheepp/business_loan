"""Audit Trail Viewer — Browse the immutable agent action log."""
import streamlit as st
import requests
import pandas as pd

API = st.session_state.get("api_url", "http://localhost:8000")

st.set_page_config(page_title="CASA — Audit Trail", page_icon="📜", layout="wide")
st.title("📜 Audit Trail")
st.markdown("Immutable log of every agent action, decision, and data transformation.")

# Filters
col1, col2 = st.columns(2)
with col1:
    app_filter = st.text_input("Filter by Application ID", placeholder="Leave empty for all")
with col2:
    limit = st.slider("Max entries", 10, 500, 100)

# Fetch
try:
    if app_filter:
        r = requests.get(f"{API}/api/dashboard/audit/{app_filter}")
    else:
        r = requests.get(f"{API}/api/dashboard/audit?limit={limit}")

    if r.status_code == 200:
        entries = r.json()
    else:
        entries = []
except Exception:
    st.error("Cannot connect to backend.")
    entries = []

if not entries:
    st.info("No audit entries yet. Submit an application and run the pipeline to generate audit logs.")
    st.stop()

# Display as table
df = pd.DataFrame(entries)
df = df[["created_at", "application_id", "agent", "action"]]
df.columns = ["Timestamp", "Application", "Agent", "Action"]

# Agent color coding
agent_colors = {
    "sarah": "🤖", "compliance": "🛡️", "underwriting": "📊",
    "document": "📄", "pricing": "💰", "orchestrator": "⚙️",
}
df["Agent"] = df["Agent"].apply(lambda x: f"{agent_colors.get(x, '❓')} {x}")

st.dataframe(df, use_container_width=True, height=500)

# Detail view
st.markdown("### Entry Details")
for entry in entries[:20]:
    agent_icon = agent_colors.get(entry["agent"], "❓")
    with st.expander(f"{agent_icon} {entry['agent']} — {entry['action']} ({entry['created_at'][:19]})"):
        st.markdown(f"**Application:** `{entry['application_id']}`")
        st.markdown(f"**Agent:** {entry['agent']}")
        st.markdown(f"**Action:** {entry['action']}")
        if entry.get("details"):
            st.json(entry["details"])
