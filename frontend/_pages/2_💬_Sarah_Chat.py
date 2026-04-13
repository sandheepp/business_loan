"""Sarah Chat — AI Engagement Agent for MSME Loan Applicants."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import requests



API = st.session_state.get("api_url", "http://localhost:8000")


# ── Header ────────────────────────────────────────────────────
st.markdown("""
<div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem;">
  <div style="width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#5B4CF5,#7B6BF8);
              display:flex;align-items:center;justify-content:center;font-size:1.4rem;">💬</div>
  <div>
    <div style="font-size:1.5rem;font-weight:800;color:#FFFFFF;letter-spacing:-0.02em;">Sarah</div>
    <div style="font-size:0.82rem;color:#00D48A;">● Online · AI Engagement Agent</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── App ID Input ──────────────────────────────────────────────
app_id = st.text_input(
    "Application ID",
    value=st.session_state.get("app_id", ""),
    placeholder="e.g. MSME3A7B2F",
    label_visibility="visible",
    key="sarah_app_id",
)

if not app_id:
    st.markdown("""
    <div class="rv-card" style="text-align:center;padding:3rem;color:#8A8FA8;">
      <div style="font-size:2.5rem;margin-bottom:0.8rem;">💬</div>
      <div style="font-size:1rem;font-weight:600;color:#FFFFFF;">Start a conversation with Sarah</div>
      <div style="font-size:0.85rem;margin-top:0.5rem;">Enter your Application ID above to get personalised guidance on your MSME loan.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Chat Session ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

# Load history on first visit
if f"loaded_{app_id}" not in st.session_state:
    try:
        r = requests.get(f"{API}/api/chat/{app_id}/history", timeout=3)
        if r.status_code == 200:
            st.session_state.messages = [
                {"role": m["role"], "content": m["content"]} for m in r.json()
            ]
    except Exception:
        pass
    st.session_state[f"loaded_{app_id}"] = True

# Show welcome message if no history
if not st.session_state.messages:
    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(91,76,245,0.1),rgba(91,76,245,0.05));
                border:1px solid rgba(91,76,245,0.25);border-radius:16px;padding:1.2rem 1.5rem;margin-bottom:1rem;">
      <div style="display:flex;align-items:flex-start;gap:0.8rem;">
        <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#5B4CF5,#7B6BF8);
                    display:flex;align-items:center;justify-content:center;font-size:0.9rem;flex-shrink:0;">💬</div>
        <div>
          <div style="font-size:0.85rem;font-weight:600;color:#FFFFFF;">Sarah</div>
          <div style="font-size:0.9rem;color:#C5C8D8;margin-top:0.3rem;line-height:1.6;">
            Namaste! I'm Sarah, your MSME loan assistant. I'm here to guide you through your secured loan application.<br><br>
            I can help you with document requirements, eligibility criteria, KYC process, DSCR calculations, and more. What would you like to know?
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Message History ───────────────────────────────────────────
for msg in st.session_state.messages:
    is_user = msg["role"] == "user"
    if is_user:
        st.markdown(f"""
        <div style="display:flex;justify-content:flex-end;margin-bottom:0.8rem;">
          <div style="background:linear-gradient(135deg,#5B4CF5,#7B6BF8);border-radius:16px 16px 4px 16px;
                      padding:0.8rem 1.2rem;max-width:70%;font-size:0.9rem;color:#FFFFFF;line-height:1.5;">
            {msg["content"]}
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex;gap:0.7rem;margin-bottom:0.8rem;">
          <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#5B4CF5,#7B6BF8);
                      display:flex;align-items:center;justify-content:center;font-size:0.85rem;flex-shrink:0;">💬</div>
          <div style="background:#1A1E35;border:1px solid rgba(255,255,255,0.07);border-radius:4px 16px 16px 16px;
                      padding:0.8rem 1.2rem;max-width:75%;font-size:0.9rem;color:#C5C8D8;line-height:1.6;">
            {msg["content"]}
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── Chat Input ────────────────────────────────────────────────
if prompt := st.chat_input("Ask Sarah about your loan application..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Sarah is typing..."):
        try:
            r = requests.post(f"{API}/api/chat/", json={
                "application_id": app_id,
                "message": prompt,
            }, timeout=30)
            if r.status_code == 200:
                response = r.json()["content"]
            else:
                response = "I'm having trouble processing your request. Please try again."
        except Exception:
            response = "I'm having trouble connecting to the server. Please ensure the backend is running."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
