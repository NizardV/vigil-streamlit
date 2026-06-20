import streamlit as st
import json
from streamlit_js_eval import streamlit_js_eval
from auth import is_authenticated, logout, fetch_user_info

st.set_page_config(page_title="Vigil", layout="wide", page_icon="🔍")

API_URL_PUBLIC = "https://vigil.projet-cyna.fr/api"

# ── Session restore via cookie httpOnly ───────────────────
if not is_authenticated():
    if not st.session_state.get("_restore_attempted"):
        # Premier rendu — lance le JS, résultat sera None
        result = streamlit_js_eval(
            js_expressions=f"""
                fetch('{API_URL_PUBLIC}/auth/session/me', {{
                    method: 'GET',
                    credentials: 'include'
                }})
                .then(r => r.ok ? r.json() : null)
                .then(data => data ? JSON.stringify(data) : null)
            """,
            key="restore_session"
        )
        if result:
            # Deuxième rendu — le JS a retourné le résultat
            data = json.loads(result)
            st.session_state["access_token"] = data["access_token"]
            st.session_state["refresh_token"] = data["refresh_token"]
            st.session_state["_restore_attempted"] = True
            fetch_user_info()
            st.rerun()
        # Si result est None, Streamlit rerun automatiquement quand le JS finit

if is_authenticated() and not st.session_state.get("user_email"):
    print(f"[DEBUG] fetching user info, access_token: {st.session_state.get('access_token', 'MISSING')[:20]}")
    fetch_user_info()
    print(f"[DEBUG] after fetch, user_email: {st.session_state.get('user_email', 'MISSING')}")

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