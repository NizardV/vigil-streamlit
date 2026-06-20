import streamlit as st
import httpx
import os
from auth import get_headers

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.set_page_config(page_title="Themes - Vigil", layout="wide")

st.title("Themes")

try:
    with httpx.Client() as client:
        themes = client.get(f"{API_URL}/themes/", headers=get_headers()).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

with st.form("add_theme"):
    st.subheader("Add a theme")
    name = st.text_input("Name")
    description = st.text_area("Description", height=80)
    keywords_raw = st.text_input("Keywords (comma-separated)")
    col1, col2 = st.columns(2)
    digest_enabled = col1.checkbox("Enable daily digest", value=True)
    digest_hour = col2.slider("Digest hour (UTC)", 0, 23, 7)
    submitted = st.form_submit_button("Create")

    if submitted and name:
        keywords = [k.strip() for k in keywords_raw.split(",") if k.strip()]
        with httpx.Client() as client:
            resp = client.post(f"{API_URL}/themes/", json={
                "name": name,
                "description": description or None,
                "keywords": keywords or None,
                "digest_hour": digest_hour,
                "digest_enabled": digest_enabled,
            }, headers=get_headers())
        if resp.status_code == 201:
            st.success(f"Theme '{name}' created.")
            st.rerun()
        else:
            st.error(f"Error: {resp.text}")

st.subheader("Configured themes")

if not themes:
    st.info("No themes yet. Create one above.")
else:
    for theme in themes:
        digest_status = "Digest enabled" if theme.get("digest_enabled", True) else "Digest disabled"
        with st.expander(f"{theme['name']} — {digest_status}"):
            st.markdown(f"**Description:** {theme.get('description') or '-'}")
            keywords = theme.get("keywords") or []
            if keywords:
                st.markdown("**Keywords:** " + " ".join([f"`{k}`" for k in keywords]))
            else:
                st.markdown("**Keywords:** -")

            col_a, col_b = st.columns(2)
            col_a.markdown(f"**Digest hour (UTC):** `{theme.get('digest_hour', 7)}:00`")
            col_b.markdown(f"**Created:** {theme['created_at'][:10]}")

            with st.form(f"edit_theme_{theme['id']}"):
                st.markdown("**Edit digest settings**")
                new_enabled = st.checkbox("Enable digest", value=theme.get("digest_enabled", True))
                new_hour = st.slider("Digest hour (UTC)", 0, 23, theme.get("digest_hour", 7))
                if st.form_submit_button("Save"):
                    with httpx.Client() as client:
                        client.patch(f"{API_URL}/themes/{theme['id']}", json={
                            "name": theme["name"],
                            "digest_enabled": new_enabled,
                            "digest_hour": new_hour,
                        }, headers=get_headers())
                    st.success("Settings saved.")
                    st.rerun()

            if st.button("Delete", key=f"del_theme_{theme['id']}"):
                with httpx.Client() as client:
                    client.delete(f"{API_URL}/themes/{theme['id']}", headers=get_headers())
                st.rerun()