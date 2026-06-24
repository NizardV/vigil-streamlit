import streamlit as st
from auth import is_authenticated, fetch_user_info, get_session_id

st.set_page_config(page_title="Vigil", layout="wide", page_icon="🔍")

# ── Auth check via nginx header ───────────────────────────
if not is_authenticated():
    st.error("Session expired. Please log in again.")
    st.markdown("[Go to Login](/login)")
    st.stop()

if not st.session_state.get("user_email"):
    fetch_user_info()

# ── Navigation ────────────────────────────────────────────
with st.sidebar:
    st.text(st.session_state.get("user_email", "User"))
    st.divider()
    st.markdown("[Logout](/logout)")

pg = st.navigation([
    st.Page("pages/home.py", title="Home", icon="🏠", default=True),
    st.Page("pages/articles.py", title="Articles", icon="📰"),
    st.Page("pages/sources.py", title="Sources", icon="📡"),
    st.Page("pages/stats.py", title="Stats", icon="📊"),
    st.Page("pages/themes.py", title="Themes", icon="🎯"),
    st.Page("pages/webhooks.py", title="Webhooks", icon="🔔"),
    st.Page("pages/settings.py", title="Settings", icon="⚙️"),
])

pg.run()