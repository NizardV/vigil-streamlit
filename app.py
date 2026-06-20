import streamlit as st
from auth import is_authenticated, logout, fetch_user_info

st.set_page_config(page_title="Vigil", layout="wide", page_icon="🔍")

API_URL_PUBLIC = "https://vigil.projet-cyna.fr/api"

# ── Session restore via query param ──────────────────────
if not is_authenticated():
    session_id = st.query_params.get("session_id")
    if session_id:
        if restore_session(session_id):
            st.query_params.clear()
            fetch_user_info()
            st.rerun()

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
            streamlit_js_eval(
                js_expressions=f"""
                    fetch('{API_URL_PUBLIC}/auth/session/me', {{
                        method: 'DELETE',
                        credentials: 'include'
                    }})
                """,
                key="delete_session"
            )
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