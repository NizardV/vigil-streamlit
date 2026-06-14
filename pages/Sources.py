import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://backend:8000/api")

st.set_page_config(page_title="Sources — WatchLLM", page_icon="📡", layout="wide")
st.title("Gestion des sources")

with httpx.Client() as client:
    themes = client.get(f"{API_URL}/themes/").json()
    sources = client.get(f"{API_URL}/sources/").json()

theme_map = {t["name"]: t["id"] for t in themes}

# ── Ajout source ──────────────────────────────────────────

with st.form("add_source"):
    st.subheader("Ajouter une source RSS")
    name = st.text_input("Nom de la source")
    url = st.text_input("URL du flux RSS")
    theme = st.selectbox("Thème", list(theme_map.keys()))
    submitted = st.form_submit_button("Ajouter")

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
            st.success(f"Source ''{name}'' ajoutée !")
            st.rerun()
        else:
            st.error("Erreur lors de l''ajout.")

# ── Liste sources ─────────────────────────────────────────

st.subheader("Sources configurées")
theme_filter = st.selectbox("Filtrer", ["Tous"] + list(theme_map.keys()))

for source in sources:
    theme_name = next((t["name"] for t in themes if t["id"] == source["theme_id"]), "?")
    if theme_filter != "Tous" and theme_name != theme_filter:
        continue

    status = "🟢" if source["active"] else "🔴"
    col1, col2, col3 = st.columns([4, 1, 1])
    col1.markdown(f"{status} **{source[''name''] or source[''url'']}** — `{theme_name}`")

    if col2.button("⏸ Toggle", key=f"toggle_{source[''id'']}"):
        with httpx.Client() as client:
            client.post(f"{API_URL}/sources/{source[''id'']}/toggle")
        st.rerun()

    if col3.button("🗑 Suppr.", key=f"del_{source[''id'']}"):
        with httpx.Client() as client:
            client.delete(f"{API_URL}/sources/{source[''id'']}")
        st.rerun()

