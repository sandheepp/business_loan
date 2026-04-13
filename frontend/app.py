"""CASA — Navigation hub. Sidebar renders once here; persists across all pages."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from styles import page_config_dark, sidebar_status

if "api_url" not in st.session_state:
    st.session_state.api_url = "http://localhost:8000"

# ── Page config + CSS — called once for all pages ─────────────
page_config_dark("CASA LOS", "🏦")

# ── Navigation — position="hidden" suppresses Streamlit's built-in nav ─
pg = st.navigation(
    [
        st.Page("home.py",                      title="Home",        icon="🏠"),
        st.Page("_pages/1_📋_Application.py",    title="Application", icon="📋"),
        st.Page("_pages/2_💬_Sarah_Chat.py",     title="Sarah Chat",  icon="💬"),
        st.Page("_pages/3_📊_Dashboard.py",      title="Dashboard",   icon="📊"),
        st.Page("_pages/4_📜_Audit_Trail.py",    title="Audit Trail", icon="📜"),
        st.Page("_pages/5_🏦_Underwriting.py",   title="Underwriting",icon="🏦"),
        st.Page("_pages/6_✅_Approvals.py",      title="Approvals",   icon="✅"),
    ],
    position="hidden",   # hide Streamlit's own nav — we use custom sidebar
)

# ── Sidebar — rendered after navigation is registered ────────────
sidebar_status()

pg.run()
