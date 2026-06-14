import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.set_page_config(page_title="Webhooks - Vigil", layout="wide")
st.title("Webhooks")

try:
    with httpx.Client() as client:
        themes = client.get(f"{API_URL}/themes/").json()
        webhooks = client.get(f"{API_URL}/webhooks/").json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

theme_map = {t["name"]: t["id"] for t in themes}

# ── Add webhook ───────────────────────────────────────────

with st.form("add_webhook"):
    st.subheader("Add a webhook")
    theme = st.selectbox("Theme", list(theme_map.keys()) if theme_map else [])
    url = st.text_input("Webhook URL", placeholder="https://discord.com/api/webhooks/...")
    wtype = st.selectbox("Type", ["discord", "slack", "custom"])
    submitted = st.form_submit_button("Add")

    if submitted and url and theme:
        with httpx.Client() as client:
            resp = client.post(f"{API_URL}/webhooks/", json={
                "theme_id": theme_map[theme],
                "url": url,
                "type": wtype,
                "active": True,
            })
        if resp.status_code == 201:
            st.success("Webhook added.")
            st.rerun()
        else:
            st.error(f"Error: {resp.text}")

# ── Test webhook ──────────────────────────────────────────

st.subheader("Configured webhooks")

if not webhooks:
    st.info("No webhooks configured yet.")
else:
    for webhook in webhooks:
        theme_name = next((t["name"] for t in themes if t["id"] == webhook["theme_id"]), "?")
        status = "🟢" if webhook["active"] else "🔴"

        col1, col2, col3 = st.columns([4, 1, 1])
        col1.markdown(f"{status} `{webhook['type']}` — **{theme_name}**  \n{webhook['url'][:60]}...")

        if col2.button("Test", key=f"test_{webhook['id']}"):
            with httpx.Client() as client:
                resp = client.post(f"{API_URL}/digests/trigger/{webhook['theme_id']}")
            if resp.status_code == 200:
                st.success("Digest triggered — check your Discord!")
            else:
                st.error(f"Error: {resp.text}")

        if col3.button("Delete", key=f"del_{webhook['id']}"):
            with httpx.Client() as client:
                client.delete(f"{API_URL}/webhooks/{webhook['id']}")
            st.rerun()