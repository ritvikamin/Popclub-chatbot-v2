"""POPclub Copilot - Streamlit frontend.

Streamlit re-runs this whole script top-to-bottom on every user interaction.
State that must survive a re-run lives in st.session_state.
"""
import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")
CHAT_URL = f"{API_URL}/api/v1/chat/query"
STATS_URL = f"{API_URL}/api/v1/chat/stats"
UPLOAD_URL = f"{API_URL}/api/v1/admin/upload"
HEALTH_URL = f"{API_URL}/health"

WELCOME = (
    "Welcome to POPclub Copilot. Ask about the UPI platform, card benefits, "
    "rewards rules, or the team - answers come straight from the source docs."
)

st.set_page_config(page_title="POPclub Copilot", page_icon="💬", layout="centered")


def backend_is_up() -> bool:
    try:
        return requests.get(HEALTH_URL, timeout=2).ok
    except requests.RequestException:
        return False


def get_stats():
    try:
        r = requests.get(STATS_URL, timeout=3)
        return r.json() if r.ok else None
    except requests.RequestException:
        return None


def error_detail(r: requests.Response) -> str:
    try:
        return r.json().get("detail", r.text)
    except ValueError:
        return r.text


# ---------- sidebar: status + document upload ----------
with st.sidebar:
    st.header("POPclub Copilot")
    if backend_is_up():
        st.success("Backend online")
        stats = get_stats()
        if stats and stats["chunks"] == 0:
            st.warning("Knowledge base is empty - upload a document below, or every answer will be a refusal.")
        elif stats:
            st.caption(f"{stats['chunks']} chunks indexed from: {', '.join(stats['sources'])}")
    else:
        st.error(f"Backend unreachable at {API_URL}")

    st.markdown("**Model:** Gemini 2.5 Flash  \n**Index:** ChromaDB (persistent)  \n**Retrieval:** top-3 chunks, cosine similarity")

    st.divider()
    st.subheader("Add to knowledge base")
    admin_key = st.text_input("Admin key", type="password", value=os.getenv("ADMIN_API_KEY", ""))
    uploaded = st.file_uploader("Upload a .txt or .md file", type=["txt", "md"])
    if uploaded:
        if st.button("Index document", type="primary"):
            with st.spinner("Chunking and embedding..."):
                try:
                    r = requests.post(
                        UPLOAD_URL,
                        files={"file": (uploaded.name, uploaded.getvalue())},
                        headers={"X-Admin-Key": admin_key},
                        timeout=120,
                    )
                    if r.ok:
                        st.session_state.upload_msg = ("success", r.json()["message"])
                    else:
                        st.session_state.upload_msg = ("error", error_detail(r))
                except requests.RequestException as e:
                    st.session_state.upload_msg = ("error", f"Upload failed: {e}")
            st.rerun()  # refresh the chunk count above
        else:
            st.caption("File selected but NOT indexed yet - click 'Index document'.")

    # Persist the last result so it doesn't vanish on the next re-run (e.g. when you chat).
    if "upload_msg" in st.session_state:
        kind, text = st.session_state.upload_msg
        getattr(st, kind)(text)

    if st.button("Clear chat"):
        st.session_state.pop("messages", None)
        st.rerun()

# ---------- chat state ----------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": WELCOME}]

st.title("POPclub Chatbot")
st.caption("Grounded on your UPI & rewards docs")


def render_message(msg: dict) -> None:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("citations"):
            with st.expander(f"Sources ({len(msg['citations'])})"):
                for c in msg["citations"]:
                    st.markdown(f"**{c['source']}** - similarity {c['score']:.0%}")
                    st.caption(c["text"])


for m in st.session_state.messages:
    render_message(m)

# ---------- handle new input ----------
if prompt := st.chat_input("Ask about UPI, cards, rewards, or the team..."):
    # Sent to the backend so follow-up questions ("what about the fee?") make sense.
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    user_msg = {"role": "user", "content": prompt}
    st.session_state.messages.append(user_msg)
    render_message(user_msg)

    with st.spinner("Searching the knowledge base..."):
        try:
            r = requests.post(CHAT_URL, json={"message": prompt, "history": history}, timeout=60)
            if r.ok:
                data = r.json()
                reply = {"role": "assistant", "content": data["answer"], "citations": data["citations"]}
            else:
                reply = {"role": "assistant", "content": f"Something went wrong: {error_detail(r)}"}
        except requests.RequestException:
            reply = {"role": "assistant", "content": "The backend did not respond. Is the FastAPI server running?"}

    st.session_state.messages.append(reply)
    render_message(reply)
