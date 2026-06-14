import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://backend:8000/api")

st.set_page_config(page_title="Themes - Vigil", layout="wide")
st.title("Themes")

with httpx.Client() as client:
    themes = client.get(f"{API_URL}/themes/").json()

# ── Add theme ─────────────────────────────────────────────

with st.form("add_theme"):
    st.subheader("Add a theme")
    name = st.text_input("Name")
    description = st.text_area("Description", height=80)
    keywords_raw = st.text_input("Keywords (comma-separated)")
    submitted = st.form_submit_button("Create")

    if submitted and name:
        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
        with httpx.Client() as client:
            resp = client.post(f"{API_URL}/themes/", json={
                "name": name,
                "description": description or None,
                "keywords": keywords or None,
            })
        if resp.status_code == 201:
            st.success(f"Theme '{name}' created.")
            st.rerun()
        else:
            st.error(f"Error: {resp.text}")

# ── Theme list ────────────────────────────────────────────

st.subheader("Configured themes")

if not themes:
    st.info("No themes yet. Create one above.")
else:
    for theme in themes:
        with st.expander(f"{theme['name']}"):
            st.markdown(f"**Description:** {theme.get('description') or '—'}")
            keywords = theme.get("keywords") or []
            if keywords:
                st.markdown("**Keywords:** " + " ".join([f"`{k}`" for k in keywords]))
            else:
                st.markdown("**Keywords:** —")
            st.caption(f"Created: {theme['created_at'][:10]}")

            col1, col2 = st.columns([1, 5])
            if col1.button("Delete", key=f"del_theme_{theme['id']}"):
                with httpx.Client() as client:
                    client.delete(f"{API_URL}/themes/{theme['id']}")
                st.rerun()