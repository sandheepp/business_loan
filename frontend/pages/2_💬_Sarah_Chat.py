"""Sarah Chat — Talk to the AI engagement agent."""
import streamlit as st
import requests
from datetime import datetime

API = st.session_state.get("api_url", "http://localhost:8000")

st.set_page_config(page_title="CASA — Sarah Chat", page_icon="💬", layout="wide")
st.title("💬 Chat with Sarah")
st.markdown("Sarah is your AI assistant throughout the loan application process.")

# App ID input
app_id = st.text_input("Application ID", value=st.session_state.get("app_id", ""),
                        placeholder="Enter your application ID")

if not app_id:
    st.info("Enter your application ID to start chatting with Sarah. "
            "You can find it on the Application page after starting an application.")
    st.stop()

# Load chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Load History"):
    try:
        r = requests.get(f"{API}/api/chat/{app_id}/history")
        if r.status_code == 200:
            st.session_state.messages = [
                {"role": m["role"], "content": m["content"]} for m in r.json()
            ]
    except Exception:
        st.warning("Could not load history.")

# Display messages
for msg in st.session_state.messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Ask Sarah anything about your application..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Sarah is typing..."):
            try:
                r = requests.post(f"{API}/api/chat/", json={
                    "application_id": app_id, "message": prompt,
                })
                if r.status_code == 200:
                    response = r.json()["content"]
                else:
                    response = "I'm having trouble connecting. Please try again."
            except Exception:
                response = "I'm having trouble connecting to the server. Is the backend running?"

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar tips
st.sidebar.markdown("### Try asking Sarah:")
st.sidebar.markdown("""
- "What documents do I need?"
- "I can't find my EIN, but I have my TIN"
- "What's the status of my application?"
- "How long will this take?"
""")
