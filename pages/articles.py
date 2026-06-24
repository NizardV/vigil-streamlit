import streamlit as st
import httpx
import os
from auth import get_headers, get_cookies

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.set_page_config(page_title="Articles - Vigil", layout="wide")

st.title("Articles")

try:
    with httpx.Client() as client:
        themes = client.get(f"{API_URL}/themes/", cookies=get_cookies()).json()
except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.stop()

# ── Semantic search ───────────────────────────────────────
search_query = st.text_input("🔍 Semantic search", placeholder="e.g. JWT authentication vulnerability")

if search_query:
    try:
        with httpx.Client(timeout=30) as client:
            articles = client.get(
                f"{API_URL}/articles/search/semantic",
                params={"q": search_query, "limit": 20},
                cookies=get_cookies()
            ).json()
        st.caption(f"{len(articles)} articles found")
        for article in articles:
            analysis = article.get("analysis") or {}
            score = analysis.get("relevance_score", 0)
            color = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"
            with st.expander(f"{color} {article['title']} - `{score}/10`"):
                st.markdown(f"**Summary:** {analysis.get('summary', '-')}")
                key_points = analysis.get('key_points') or []
                if key_points:
                    st.markdown("**Key points:**")
                    for point in key_points:
                        st.markdown(f"- {point}")
                st.markdown(f"**Theme match:** `{analysis.get('theme_match', '-')}`")
                st.markdown(f"[Read article]({article['url']})")
                st.divider()
                fb_col1, fb_col2, fb_col3 = st.columns([1, 1, 4])
                if fb_col1.button("👍 Relevant", key=f"s_like_{article['id']}"):
                    with httpx.Client() as client:
                        client.post(f"{API_URL}/feedback/", json={"article_id": article["id"], "rating": 1}, cookies=get_cookies())
                    st.success("Feedback saved.")
                    st.rerun()
                if fb_col2.button("👎 Not relevant", key=f"s_dislike_{article['id']}"):
                    with httpx.Client() as client:
                        client.post(f"{API_URL}/feedback/", json={"article_id": article["id"], "rating": -1}, cookies=get_cookies())
                    st.rerun()
                comment = st.text_input("💬 Comment (optional)", key=f"s_comment_{article['id']}")
                if st.button("Save comment", key=f"s_save_comment_{article['id']}") and comment:
                    with httpx.Client() as client:
                        client.post(f"{API_URL}/feedback/", json={"article_id": article["id"], "rating": 1, "comment": comment}, cookies=get_cookies())
                    st.success("Comment saved.")
                    st.rerun()
        st.stop()
    except Exception as e:
        st.error(f"Search error: {e}")

# ── Filters ───────────────────────────────────────────────
theme_options = {t["name"]: t["id"] for t in themes}
theme_options["All"] = None

col1, col2 = st.columns([2, 1])
selected_theme = col1.selectbox("Filter by theme", list(theme_options.keys()))
min_score = col2.slider("Minimum score", 1.0, 10.0, 1.0, 0.5)

theme_id = theme_options[selected_theme]

# ── Article list ──────────────────────────────────────────
params = {"limit": 50}
if theme_id:
    params["theme_id"] = theme_id

try:
    with httpx.Client() as client:
        articles = client.get(f"{API_URL}/articles/", params=params, cookies=get_cookies()).json()
except Exception as e:
    st.error(f"Could not load articles: {e}")
    st.stop()

filtered = [
    a for a in articles
    if a.get("analysis") and a["analysis"]["relevance_score"] >= min_score
]

st.caption(f"{len(filtered)} articles displayed")

if not filtered:
    st.info("No articles match the current filters.")
    st.stop()

for article in filtered:
    analysis = article.get("analysis", {})
    score = analysis.get("relevance_score", 0)
    color = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"

    with st.expander(f"{color} {article['title']} - `{score}/10`"):
        st.markdown(f"**Summary:** {analysis.get('summary', '-')}")

        key_points = analysis.get('key_points', [])
        if key_points:
            st.markdown("**Key points:**")
            for point in key_points:
                st.markdown(f"- {point}")

        st.markdown(f"**Theme match:** `{analysis.get('theme_match', '-')}`")
        st.markdown(f"[Read article]({article['url']})")

        st.divider()
        fb_col1, fb_col2, _ = st.columns([1, 1, 4])

        if fb_col1.button("👍 Relevant", key=f"like_{article['id']}"):
            with httpx.Client() as client:
                client.post(f"{API_URL}/feedback/", json={"article_id": article["id"], "rating": 1}, cookies=get_cookies())
            st.success("Feedback saved.")
            st.rerun()

        if fb_col2.button("👎 Not relevant", key=f"dislike_{article['id']}"):
            with httpx.Client() as client:
                client.post(f"{API_URL}/feedback/", json={"article_id": article["id"], "rating": -1}, cookies=get_cookies())
            st.rerun()

        comment = st.text_input("💬 Comment (optional)", key=f"comment_{article['id']}")
        if st.button("Save comment", key=f"save_comment_{article['id']}") and comment:
            with httpx.Client() as client:
                client.post(f"{API_URL}/feedback/", json={"article_id": article["id"], "rating": 1, "comment": comment}, cookies=get_cookies())
            st.success("Comment saved.")
            st.rerun()