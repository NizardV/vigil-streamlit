import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

API_URL = os.getenv("API_URL", "http://backend:8000/api")

st.set_page_config(page_title="Stats - Vigil", layout="wide")
st.title("Statistics")

try:
    with httpx.Client() as client:
        articles = client.get(f"{API_URL}/articles/?limit=500").json()
        themes = client.get(f"{API_URL}/themes/").json()
        digests = client.get(f"{API_URL}/digests/").json()

    theme_map = {t["id"]: t["name"] for t in themes}
    processed = [a for a in articles if a.get("analysis")]

    if not processed:
        st.info("No analyzed articles yet.")
        st.stop()

    # ── Build dataframe ───────────────────────────────────

    rows = []
    for a in processed:
        rows.append({
            "title": a["title"],
            "url": a["url"],
            "score": a["analysis"]["relevance_score"],
            "theme_match": a["analysis"].get("theme_match", "Unknown"),
            "fetched_at": a["fetched_at"][:10],
        })

    df = pd.DataFrame(rows)

    # ── Global metrics ────────────────────────────────────

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total articles", len(articles))
    col2.metric("Analyzed", len(processed))
    col3.metric("Avg score", f"{df['score'].mean():.1f}/10")
    col4.metric("Digests sent", len(digests))

    st.divider()

    col_left, col_right = st.columns(2)

    # ── Score distribution ────────────────────────────────

    with col_left:
        st.subheader("Score distribution")
        fig = px.histogram(
            df, x="score", nbins=10, range_x=[1, 10],
            color_discrete_sequence=["#5865F2"]
        )
        fig.update_layout(
            bargap=0.1,
            xaxis_title="Score",
            yaxis_title="Articles",
            margin=dict(t=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Articles per theme ────────────────────────────────

    with col_right:
        st.subheader("Articles by theme")
        theme_counts = df["theme_match"].value_counts().reset_index()
        theme_counts.columns = ["theme", "count"]
        fig2 = px.pie(
            theme_counts, names="theme", values="count",
            color_discrete_sequence=px.colors.sequential.Blues_r
        )
        fig2.update_layout(margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Score over time ───────────────────────────────────

    st.subheader("Average score over time")
    df_time = df.groupby("fetched_at")["score"].mean().reset_index()
    df_time.columns = ["date", "avg_score"]
    fig3 = px.line(
        df_time, x="date", y="avg_score",
        markers=True, color_discrete_sequence=["#5865F2"]
    )
    fig3.update_layout(
        xaxis_title="Date",
        yaxis_title="Avg score",
        yaxis_range=[1, 10],
        margin=dict(t=20)
    )
    st.plotly_chart(fig3, use_container_width=True)

    # ── Top articles ──────────────────────────────────────

    st.subheader("Top 10 articles by score")
    top_df = df.nlargest(10, "score")[["title", "score", "theme_match", "fetched_at"]]
    top_df.columns = ["Title", "Score", "Theme", "Date"]
    st.dataframe(top_df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.info("Make sure the backend is running.")