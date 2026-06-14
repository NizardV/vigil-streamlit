import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.set_page_config(page_title="Sources - Vigil", layout="wide")
st.title("Sources")

try:
    with httpx.Client() as client:
        themes = client.get(f"{API_URL}/themes/").json()
        sources = client.get(f"{API_URL}/sources/").json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

theme_map = {t["name"]: t["id"] for t in themes}

# ── Add source ────────────────────────────────────────────

with st.form("add_source"):
    st.subheader("Add a RSS source")
    name = st.text_input("Source name")
    url = st.text_input("RSS feed URL")
    theme = st.selectbox("Theme", list(theme_map.keys()) if theme_map else [])
    submitted = st.form_submit_button("Add")

    if submitted and url and theme:
        with httpx.Client() as client:
            resp = client.post(f"{API_URL}/sources/", json={
                "name": name,
                "url": url,
                "theme_id": theme_map[theme],
                "type": "rss",
                "active": True,
            })
        if resp.status_code == 201:
            st.success(f"Source '{name}' added.")
            st.rerun()
        else:
            st.error(f"Error: {resp.text}")

# ── Source list ───────────────────────────────────────────

st.subheader("Configured sources")

if not themes:
    st.info("No themes yet. Create one in the Themes page first.")
    st.stop()

theme_filter = st.selectbox("Filter by theme", ["All"] + list(theme_map.keys()))

for source in sources:
    theme_name = next((t["name"] for t in themes if t["id"] == source["theme_id"]), "?")
    if theme_filter != "All" and theme_name != theme_filter:
        continue

    status = "🟢" if source["active"] else "🔴"
    col1, col2, col3 = st.columns([4, 1, 1])
    col1.markdown(f"{status} **{source['name'] or source['url']}** — `{theme_name}`")

    if col2.button("Toggle", key=f"toggle_{source['id']}"):
        with httpx.Client() as client:
            client.post(f"{API_URL}/sources/{source['id']}/toggle")
        st.rerun()

    if col3.button("Delete", key=f"del_{source['id']}"):
        with httpx.Client() as client:
            client.delete(f"{API_URL}/sources/{source['id']}")
        st.rerun()