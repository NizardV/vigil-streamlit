import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://backend:8000/api")

st.set_page_config(page_title="Articles — WatchLLM", page_icon="📰", layout="wide")
st.title("Articles")

# ── Filtres ───────────────────────────────────────────────

with httpx.Client() as client:
    themes = client.get(f"{API_URL}/themes/").json()

theme_options = {t["name"]: t["id"] for t in themes}
theme_options["Tous"] = None

col1, col2 = st.columns([2, 1])
selected_theme = col1.selectbox("Filtrer par thème", list(theme_options.keys()))
min_score = col2.slider("Score minimum", 1.0, 10.0, 1.0, 0.5)

theme_id = theme_options[selected_theme]

# ── Liste articles ────────────────────────────────────────

params = {"limit": 50}
if theme_id:
    params["theme_id"] = theme_id

with httpx.Client() as client:
    articles = client.get(f"{API_URL}/articles/", params=params).json()

filtered = [
    a for a in articles
    if a.get("analysis") and a["analysis"]["relevance_score"] >= min_score
]

st.caption(f"{len(filtered)} articles affichés")

for article in filtered:
    analysis = article.get("analysis", {})
    score = analysis.get("relevance_score", 0)
    color = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"

    with st.expander(f"{color} {article[''title'']} — `{score}/10`"):
        st.markdown(f"**Résumé :** {analysis.get(''summary'', ''—'')}")
        st.markdown(f"**Thème détecté :** `{analysis.get(''theme_match'', ''—'')}`")
        st.markdown(f"[🔗 Lire l''article]({article[''url'']})")

        # ── Feedback ──────────────────────────────────────
        st.divider()
        fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 4])

        if fb_col1.button("👍 Pertinent", key=f"like_{article[''id'']}"):
            with httpx.Client() as client:
                client.post(f"{API_URL}/feedback/", json={
                    "article_id": article["id"],
                    "rating": 1
                })
            st.success("Feedback enregistré !")

        if fb_col2.button("👎 Non pertinent", key=f"dislike_{article[''id'']}"):
            with httpx.Client() as client:
                client.post(f"{API_URL}/feedback/", json={
                    "article_id": article["id"],
                    "rating": -1
                })
            st.warning("Feedback enregistré.")

