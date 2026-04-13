"""Revolut-inspired design system — shared CSS for all pages."""

REVOLUT_CSS = """
<style>
/* ── Google Fonts ───────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ─────────────────────────────────────── */
:root {
  --bg-primary:    #0C0F1E;
  --bg-secondary:  #131729;
  --bg-card:       #1A1E35;
  --bg-card-hover: #1F2440;
  --accent:        #5B4CF5;
  --accent-light:  #7B6BF8;
  --accent-glow:   rgba(91, 76, 245, 0.25);
  --green:         #00D48A;
  --green-bg:      rgba(0, 212, 138, 0.12);
  --red:           #FF3B57;
  --red-bg:        rgba(255, 59, 87, 0.12);
  --amber:         #F5A623;
  --amber-bg:      rgba(245, 166, 35, 0.12);
  --blue:          #3B9EF5;
  --blue-bg:       rgba(59, 158, 245, 0.12);
  --text-primary:  #FFFFFF;
  --text-secondary:#8A8FA8;
  --text-muted:    #4A4E6A;
  --border:        rgba(255, 255, 255, 0.07);
  --border-strong: rgba(255, 255, 255, 0.15);
  --radius-sm:     8px;
  --radius-md:     12px;
  --radius-lg:     18px;
  --radius-xl:     24px;
  --shadow:        0 4px 24px rgba(0,0,0,0.35);
  --shadow-accent: 0 4px 20px rgba(91,76,245,0.3);
}

/* ── Global Reset ───────────────────────────────────────── */
html, body, [data-testid="stApp"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Sidebar ────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D1025 0%, #0F1228 60%, #0C0F1E 100%) !important;
    border-right: 1px solid rgba(91,76,245,0.2) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] p {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
}

/* ── Search box ───────────────────────────────────────── */
section[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(91,76,245,0.25) !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-size: 0.82rem !important;
}
section[data-testid="stSidebar"] input:focus {
    border-color: rgba(91,76,245,0.55) !important;
    box-shadow: 0 0 0 2px rgba(91,76,245,0.15) !important;
    outline: none !important;
}

/* ── Hide Streamlit's default nav — we build our own ─── */
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    display: none !important;
}
/* Hide the search input that came with nav */
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] input,
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] {
    display: none !important;
}

/* Suppress layout flash during page transitions — no animated reflows */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] * {
    transition: none !important;
    animation-duration: 0s !important;
}

/* ── User content fills the full sidebar height ──────── */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
    flex: 1 !important;
    display: flex !important;
    flex-direction: column !important;
    padding: 0 !important;
    overflow-y: auto !important;
}

/* ── Custom page_link buttons ─────────────────────────── */
section[data-testid="stSidebar"] [data-testid="stPageLink"] {
    border-radius: 10px !important;
    border: 1px solid transparent !important;
    margin: 1px 0 !important;
    transition: background 0.15s, border-color 0.15s !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
    background: rgba(91,76,245,0.14) !important;
    border-color: rgba(91,76,245,0.3) !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"] {
    padding: 0.5rem 0.8rem !important;
    border-radius: 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]:hover {
    background: rgba(91,76,245,0.14) !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"],
section[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"].active {
    background: linear-gradient(135deg,rgba(91,76,245,0.25),rgba(91,76,245,0.07)) !important;
    border-color: rgba(91,76,245,0.45) !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"] p {
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    color: #C8CADC !important;
}
section[data-testid="stSidebar"] [data-testid="stPageLink"]:hover p {
    color: #FFFFFF !important;
}

/* ── Main Content ───────────────────────────────────────── */
[data-testid="block-container"] {
    padding-top: 1.5rem !important;
}

/* ── Typography ─────────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.02em !important;
}
p, span, div, label {
    font-family: 'Inter', sans-serif !important;
}

/* ── Input Fields ───────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.65rem 1rem !important;
    font-size: 0.9rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-glow) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder {
    color: var(--text-muted) !important;
}

/* ── Select Box ─────────────────────────────────────────── */
.stSelectbox > div > div {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}
.stSelectbox > div > div > div {
    color: var(--text-primary) !important;
}

/* ── Number Input ───────────────────────────────────────── */
.stNumberInput > div > div > input {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
}

/* ── Labels ─────────────────────────────────────────────── */
.stTextInput label, .stSelectbox label, .stNumberInput label,
.stTextArea label, .stSlider label, .stFileUploader label {
    color: var(--text-secondary) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    text-transform: uppercase !important;
    margin-bottom: 0.3rem !important;
}

/* ── Buttons ────────────────────────────────────────────── */
.stButton > button {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: -0.01em !important;
}
.stButton > button:hover {
    background-color: var(--bg-card-hover) !important;
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--accent), var(--accent-light)) !important;
    border: none !important;
    box-shadow: var(--shadow-accent) !important;
    color: white !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #4a3de0, var(--accent)) !important;
    box-shadow: 0 6px 24px rgba(91,76,245,0.45) !important;
}

/* ── Slider ─────────────────────────────────────────────── */
.stSlider > div > div > div > div {
    background-color: var(--accent) !important;
}

/* ── Metrics ────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1rem 1.2rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}

/* ── Expanders ──────────────────────────────────────────── */
.streamlit-expanderHeader {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    color: var(--text-primary) !important;
    font-weight: 600 !important;
}
.streamlit-expanderContent {
    background-color: var(--bg-secondary) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── File Uploader ──────────────────────────────────────── */
[data-testid="stFileUploader"] {
    background-color: var(--bg-card) !important;
    border: 2px dashed var(--border-strong) !important;
    border-radius: var(--radius-lg) !important;
    padding: 1.5rem !important;
    text-align: center !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── Progress Bar ───────────────────────────────────────── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent), var(--accent-light)) !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background-color: var(--bg-card) !important;
    border-radius: 4px !important;
}

/* ── Divider ────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ── Alerts / Info boxes ────────────────────────────────── */
.stAlert {
    border-radius: var(--radius-md) !important;
    border: none !important;
}
.stSuccess {
    background-color: var(--green-bg) !important;
    color: var(--green) !important;
}
.stError {
    background-color: var(--red-bg) !important;
    color: var(--red) !important;
}
.stWarning {
    background-color: var(--amber-bg) !important;
    color: var(--amber) !important;
}
.stInfo {
    background-color: var(--blue-bg) !important;
    color: var(--blue) !important;
}

/* ── Dataframe ──────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] th {
    background-color: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stDataFrame"] td {
    color: var(--text-primary) !important;
    background-color: var(--bg-secondary) !important;
}

/* ── Chat Messages ──────────────────────────────────────── */
[data-testid="chat-message"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
}

/* ── Custom Component Classes ───────────────────────────── */
.rv-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
.rv-card-accent {
    border-left: 3px solid var(--accent);
}
.rv-card-green {
    border-left: 3px solid var(--green);
    background: linear-gradient(135deg, var(--bg-card), rgba(0,212,138,0.05));
}
.rv-card-red {
    border-left: 3px solid var(--red);
    background: linear-gradient(135deg, var(--bg-card), rgba(255,59,87,0.05));
}
.rv-card-amber {
    border-left: 3px solid var(--amber);
    background: linear-gradient(135deg, var(--bg-card), rgba(245,166,35,0.05));
}

.rv-metric-big {
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.04em;
    line-height: 1;
}
.rv-metric-label {
    font-size: 0.75rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.3rem;
}
.rv-metric-sub {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}

.rv-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.25rem 0.75rem;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.rv-badge-green  { background: var(--green-bg);  color: var(--green); }
.rv-badge-red    { background: var(--red-bg);    color: var(--red); }
.rv-badge-amber  { background: var(--amber-bg);  color: var(--amber); }
.rv-badge-accent { background: var(--accent-glow); color: var(--accent-light); }
.rv-badge-blue   { background: var(--blue-bg);   color: var(--blue); }
.rv-badge-muted  { background: rgba(255,255,255,0.07); color: var(--text-secondary); }

.rv-hero {
    background: linear-gradient(135deg, var(--bg-card) 0%, rgba(91,76,245,0.15) 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
}
.rv-hero-title {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.04em;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #FFFFFF 0%, #A09BFF 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.rv-hero-sub {
    font-size: 1.1rem;
    color: var(--text-secondary);
    font-weight: 400;
    max-width: 500px;
}

.rv-section-title {
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.8rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

.rv-step-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.4rem 1rem;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
}
.rv-step-active  { background: linear-gradient(135deg, #5B4CF5, #8B7FF8); color: white; box-shadow: 0 4px 15px rgba(91,76,245,0.45); }
.rv-step-done    { background: linear-gradient(135deg, rgba(0,212,138,0.15), rgba(0,212,138,0.05)); color: var(--green); border: 1px solid rgba(0,212,138,0.35); }
.rv-step-pending { background: var(--bg-card); color: var(--text-muted); border: 1px solid var(--border); }

.rv-pipeline-stage {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
    margin-bottom: 0.5rem;
    transition: all 0.2s;
}
.rv-pipeline-stage:hover {
    border-color: var(--border-strong);
    background: var(--bg-card-hover);
}
.rv-pipeline-stage.active {
    border-color: var(--accent);
    background: linear-gradient(135deg, var(--bg-card), rgba(91,76,245,0.1));
}
.rv-pipeline-stage.done {
    border-color: rgba(0,212,138,0.3);
}

.rv-stat-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.9rem;
}
.rv-stat-row:last-child { border-bottom: none; }
.rv-stat-label { color: var(--text-secondary); }
.rv-stat-value { color: var(--text-primary); font-weight: 600; }

.rv-app-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.3rem 1.5rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s;
    cursor: pointer;
}
.rv-app-card:hover {
    border-color: var(--accent);
    background: var(--bg-card-hover);
    transform: translateY(-1px);
    box-shadow: var(--shadow);
}
.rv-app-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
}
.rv-app-meta {
    font-size: 0.82rem;
    color: var(--text-secondary);
    margin-top: 0.2rem;
}
.rv-amount {
    font-size: 1.3rem;
    font-weight: 800;
    color: var(--text-primary);
    letter-spacing: -0.02em;
}

.rv-form-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.8rem;
    margin-bottom: 1.2rem;
}
.rv-form-section-title {
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Suppress page-transition skeleton & loading states ── */
/* The skeleton appears after 500 ms while new page loads — hide it
   entirely since we have a fast local connection and it causes jitter. */
[data-testid="stAppSkeleton"],
.stAppSkeleton {
    display: none !important;
}

/* Individual skeleton shimmer bars */
[data-testid="stSkeleton"],
.stSkeleton {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 6px !important;
}

/* Keep background dark so there's no white flash between pages */
html, body {
    background-color: var(--bg-primary) !important;
}
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stAppViewMain"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewBlockContainer"] {
    background-color: var(--bg-primary) !important;
    min-height: 100vh !important;
}

/* Status widget (spinning indicator top-right) */
[data-testid="stStatusWidget"] {
    display: none !important;
}
</style>
"""


def page_config_dark(title: str, icon: str = "🏦"):
    """Standard page config for dark theme pages."""
    import streamlit as st
    st.set_page_config(
        page_title=f"CASA — {title}",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(REVOLUT_CSS, unsafe_allow_html=True)


def sidebar_status():
    """Render full custom sidebar: landing link, nav, status pinned at bottom."""
    import streamlit as st
    import requests
    api = st.session_state.get("api_url", "http://localhost:8000")
    try:
        r = requests.get(f"{api}/health", timeout=2)
        ok = r.status_code == 200
    except Exception:
        ok = False

    color  = "#00D48A" if ok else "#FF3B57"
    bg     = "rgba(0,212,138,0.08)" if ok else "rgba(255,59,87,0.08)"
    border = "rgba(0,212,138,0.22)" if ok else "rgba(255,59,87,0.22)"
    label  = "Backend Connected" if ok else "Backend Offline"
    pulse  = "animation:pulse 2s infinite;" if ok else ""

    # ── Top: CASA logo + landing link ─────────────────────────
    st.sidebar.markdown(f"""
<style>
@keyframes pulse {{
  0%,100% {{ opacity:1; }}
  50%      {{ opacity:0.4; }}
}}
</style>
<div style="padding:1rem 0.85rem 0.8rem;">
  <!-- CASA branding -->
  <div style="display:flex;align-items:center;gap:0.55rem;margin-bottom:0.9rem;">
    <div style="width:30px;height:30px;border-radius:8px;flex-shrink:0;
                background:linear-gradient(135deg,#5B4CF5,#8B7FF8);
                display:flex;align-items:center;justify-content:center;font-size:0.95rem;
                box-shadow:0 3px 10px rgba(91,76,245,0.38);">🏦</div>
    <div>
      <div style="font-size:1.05rem;font-weight:900;letter-spacing:-0.03em;
                  background:linear-gradient(135deg,#FFFFFF 30%,#A09BFF);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  background-clip:text;line-height:1.1;">CASA</div>
      <div style="font-size:0.62rem;color:#5A5E7A;font-weight:500;letter-spacing:0.02em;">
        MSME Loan Origination</div>
    </div>
  </div>

  <!-- Landing page link -->
  <a href="/landingpage" target="_self" style="
    display:flex;align-items:center;gap:0.6rem;
    padding:0.5rem 0.8rem;
    background:rgba(255,255,255,0.04);
    border:1px solid rgba(255,255,255,0.09);
    border-radius:10px;text-decoration:none;
    font-size:0.83rem;font-weight:600;color:#C8CADC;
    transition:background 0.15s,border-color 0.15s;">
    <span style="font-size:0.88rem;">🏠</span>
    <span style="flex:1;">Landing Page</span>
    <span style="font-size:0.7rem;color:#4A4E6A;">↗</span>
  </a>
</div>

<!-- Section label -->
<div style="padding:0 0.85rem 0.3rem;
            font-size:0.65rem;font-weight:700;color:#3A3E58;
            text-transform:uppercase;letter-spacing:0.12em;">Navigation</div>
""", unsafe_allow_html=True)

    # ── Middle: page links ─────────────────────────────────────
    pages = [
        ("/Application",  "📋", "Application"),
        ("/Sarah_Chat",   "💬", "Sarah Chat"),
        ("/Dashboard",    "📊", "Dashboard"),
        ("/Audit_Trail",  "📜", "Audit Trail"),
        ("/Underwriting", "🏦", "Underwriting"),
        ("/Approvals",    "✅", "Approvals"),
    ]
    nav_links_html = '<div style="padding:0 0.5rem 0.5rem;">'
    for href, icon, label_text in pages:
        nav_links_html += f"""
<a href="{href}" target="_self" style="
  display:flex;align-items:center;gap:0.6rem;
  padding:0.5rem 0.8rem;margin-bottom:0.2rem;
  background:rgba(255,255,255,0.03);
  border:1px solid rgba(255,255,255,0.06);
  border-radius:10px;text-decoration:none;
  font-size:0.83rem;font-weight:600;color:#C8CADC;
  transition:background 0.15s,border-color 0.15s;">
  <span style="font-size:0.88rem;">{icon}</span>
  <span style="flex:1;">{label_text}</span>
</a>"""
    nav_links_html += '</div>'
    st.sidebar.markdown(nav_links_html, unsafe_allow_html=True)

    # ── Bottom: backend status (sticky to bottom) ──────────────
    st.sidebar.markdown(f"""
<div style="margin-top:auto;padding:0.85rem 0.85rem 1rem;">
  <div style="padding:0.5rem 0.75rem;
              background:{bg};border:1px solid {border};border-radius:10px;
              display:flex;align-items:center;gap:0.55rem;">
    <span style="width:7px;height:7px;border-radius:50%;background:{color};
                 display:inline-block;flex-shrink:0;{pulse}"></span>
    <span style="font-size:0.74rem;color:#8A8FA8;font-weight:500;">{label}</span>
  </div>
</div>
""", unsafe_allow_html=True)


def badge(text: str, color: str = "accent") -> str:
    """Return HTML badge string."""
    return f'<span class="rv-badge rv-badge-{color}">{text}</span>'


def status_badge(status: str) -> str:
    """Return a color-coded status badge."""
    mapping = {
        "lead_created":          ("New Lead", "blue"),
        "application_draft":     ("Draft", "muted"),
        "application_submitted": ("Submitted", "accent"),
        "kyc_pending":           ("KYC Pending", "amber"),
        "kyc_in_review":         ("KYC Review", "amber"),
        "kyc_verified":          ("KYC Verified", "green"),
        "kyc_failed":            ("KYC Failed", "red"),
        "document_collection":   ("Docs Needed", "amber"),
        "document_review":       ("Doc Review", "amber"),
        "data_extraction":       ("Extracting Data", "blue"),
        "data_enrichment":       ("Enrichment", "blue"),
        "financial_analysis":    ("Financials", "blue"),
        "collateral_assessment": ("Collateral", "blue"),
        "underwriting":          ("Underwriting", "accent"),
        "cam_draft":             ("CAM Draft", "accent"),
        "cam_finalized":         ("CAM Done", "accent"),
        "pending_bcm":           ("Pending BCM", "amber"),
        "pending_rch":           ("Pending RCH", "amber"),
        "pending_cc":            ("Credit Comm.", "amber"),
        "sanctioned":            ("Sanctioned", "green"),
        "sanction_accepted":     ("Accepted", "green"),
        "legal_docs":            ("Legal Docs", "blue"),
        "legal_verified":        ("Legal OK", "green"),
        "disbursement_pending":  ("Disburse Pending", "amber"),
        "disbursed":             ("Disbursed", "green"),
        "monitoring":            ("Monitoring", "green"),
        "declined":              ("Declined", "red"),
        "withdrawn":             ("Withdrawn", "muted"),
    }
    text, color = mapping.get(status, (status.replace("_", " ").title(), "muted"))
    return badge(text, color)


def format_inr(amount: float) -> str:
    """Format amount in Indian numbering system."""
    if amount >= 10_000_000:
        return f"₹{amount/10_000_000:.1f} Cr"
    elif amount >= 100_000:
        return f"₹{amount/100_000:.1f} L"
    elif amount >= 1_000:
        return f"₹{amount/1_000:.1f}K"
    return f"₹{amount:,.0f}"
