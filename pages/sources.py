import streamlit as st
import httpx
import os
from auth import get_headers, get_cookies

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.set_page_config(page_title="Sources - Vigil", layout="wide")

st.title("Sources")

SOURCE_ICONS = {
    "rss": "📡",
    "youtube": "▶️",
    "reddit": "🔴",
    "github": "🐙",
    "hackernews": "🔶",
}

try:
    with httpx.Client() as client:
        themes = client.get(f"{API_URL}/themes/", cookies=get_cookies()).json()
        sources = client.get(f"{API_URL}/sources/", cookies=get_cookies()).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

theme_map = {t["name"]: t["id"] for t in themes}

# ── Add source ────────────────────────────────────────────
with st.expander("➕ Add a source", expanded=True):
    with st.form("add_source"):
        st.caption("Paste any URL — RSS feed, YouTube channel, Reddit subreddit, GitHub repo, or Hacker News keyword (hn:python)")
        name = st.text_input("Source name (optional)")
        url = st.text_input("URL")
        theme = st.selectbox("Theme", list(theme_map.keys()) if theme_map else [])
        fetch_interval = st.select_slider(
            "Fetch interval",
            options=[1, 2, 6, 12, 24],
            value=2,
            format_func=lambda x: f"Every {x}h"
        )
        submitted = st.form_submit_button("Add source")

        if submitted:
            if not url:
                st.error("Please enter a URL.")
            elif not theme_map:
                st.error("Create a theme first.")
            else:
                with st.spinner("Validating source..."):
                    with httpx.Client(timeout=15) as client:
                        resp = client.post(f"{API_URL}/sources/", json={
                            "name": name or url,
                            "url": url,
                            "theme_id": theme_map[theme],
                            "type": "rss",
                            "active": True,
                            "fetch_interval_hours": fetch_interval,
                        }, cookies=get_cookies())
                if resp.status_code == 201:
                    data = resp.json()
                    st.success(f"Source added as **{data['type'].upper()}** — {data['url']}")
                    st.rerun()
                else:
                    detail = resp.json().get("detail", resp.text)
                    st.error(f"Error: {detail}")

# ── Source list ───────────────────────────────────────────
st.subheader("Configured sources")

if not themes:
    st.info("No themes yet. Create one in the Themes page first.")
    st.stop()

if not sources:
    st.info("No sources yet. Add one above.")
    st.stop()

theme_filter = st.selectbox("Filter by theme", ["All"] + list(theme_map.keys()))

for source in sources:
    theme_name = next((t["name"] for t in themes if t["id"] == source["theme_id"]), "?")
    if theme_filter != "All" and theme_name != theme_filter:
        continue

    status = "🟢" if source["active"] else "🔴"
    source_icon = SOURCE_ICONS.get(source.get("type", "rss"), "📡")
    interval = source.get("fetch_interval_hours", 2)

    col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
    col1.markdown(f"{status} {source_icon} **{source['name'] or source['url']}** — `{theme_name}` — every `{interval}h`")

    if col2.button("Toggle", key=f"toggle_{source['id']}"):
        with httpx.Client() as client:
            client.post(f"{API_URL}/sources/{source['id']}/toggle", cookies=get_cookies())
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
            }, cookies=get_cookies())
        st.rerun()

    if col4.button("🗑️", key=f"del_{source['id']}"):
        with httpx.Client() as client:
            client.delete(f"{API_URL}/sources/{source['id']}", cookies=get_cookies())
        st.rerun()