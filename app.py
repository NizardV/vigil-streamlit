import streamlit as st
from streamlit_cookies_controller import CookieController
from auth import is_authenticated, logout, fetch_user_info, refresh_access_token

st.set_page_config(page_title="Vigil", layout="wide", page_icon="🔍")

cookie = CookieController()

# ── Session restore from cookie ───────────────────────────
if not is_authenticated():
    refresh_token = cookie.get("vigil_refresh_token")
    if refresh_token:
        st.session_state["refresh_token"] = refresh_token
        if refresh_access_token():
            fetch_user_info()

if is_authenticated() and not st.session_state.get("user_email"):
    fetch_user_info()

# ── Navigation ────────────────────────────────────────────

if not is_authenticated():
    pg = st.navigation([
        st.Page("login.py", title="Login", icon="🔐"),
        st.Page("email_confirmed.py", title="Email Confirmed", url_path="email-confirmed")
    ], position="hidden")
else:
    with st.sidebar:
        st.text(st.session_state.get('user_email', 'User'))
        st.divider()
        if st.button("Logout", use_container_width=True):
            cookie.remove("vigil_refresh_token")
            logout()

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