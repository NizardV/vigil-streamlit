import streamlit as st
import httpx
import os
from auth import require_auth, get_headers

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.set_page_config(page_title="Sources - Vigil", layout="wide")

require_auth()

st.title("Sources")

try:
    with httpx.Client() as client:
        themes = client.get(f"{API_URL}/themes/", headers=get_headers()).json()
        sources = client.get(f"{API_URL}/sources/", headers=get_headers()).json()
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
    fetch_interval = st.select_slider(
        "Fetch interval",
        options=[1, 2, 6, 12, 24],
        value=2,
        format_func=lambda x: f"Every {x}h"
    )
    submitted = st.form_submit_button("Add")

    if submitted and url and theme:
        with httpx.Client() as client:
            resp = client.post(f"{API_URL}/sources/", json={
                "name": name,
                "url": url,
                "theme_id": theme_map[theme],
                "type": "rss",
                "active": True,
                "fetch_interval_hours": fetch_interval,
            }, headers=get_headers())
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
    interval = source.get("fetch_interval_hours", 2)

    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    col1.markdown(f"{status} **{source['name'] or source['url']}** — `{theme_name}` — every `{interval}h`")

    if col2.button("Toggle", key=f"toggle_{source['id']}"):
        with httpx.Client() as client:
            client.post(f"{API_URL}/sources/{source['id']}/toggle", headers=get_headers())
        st.rerun()

    new_interval = col3.selectbox(
        "Interval",
        [1, 2, 6, 12, 24],
        index=[1, 2, 6, 12, 24].index(interval) if interval in [1, 2, 6, 12, 24] else 1,
        key=f"interval_{source['id']}",
        label_visibility="collapsed"
    )
    if new_interval != interval:
        with httpx.Client() as client:
            client.patch(f"{API_URL}/sources/{source['id']}", json={
                "theme_id": source["theme_id"],
                "url": source["url"],
                "fetch_interval_hours": new_interval,
            }, headers=get_headers())
        st.rerun()

    if col4.button("Delete", key=f"del_{source['id']}"):
        with httpx.Client() as client:
            client.delete(f"{API_URL}/sources/{source['id']}", headers=get_headers())
        st.rerun()