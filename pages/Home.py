import streamlit as st
import httpx
import pandas as pd
import plotly.express as px
import os

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.set_page_config(page_title="Vigil", layout="wide")
st.title("Vigil - Tech Watch Dashboard")
st.caption("Automated tech watch system with LLM scoring and feedback loop")

col1, col2, col3, col4 = st.columns(4)

try:
    with httpx.Client() as client:
        articles = client.get(f"{API_URL}/articles/?limit=500").json()
        themes = client.get(f"{API_URL}/themes/").json()
        sources = client.get(f"{API_URL}/sources/").json()
        digests = client.get(f"{API_URL}/digests/").json()

    processed = [a for a in articles if a["processed"]]
    scores = [a["analysis"]["relevance_score"] for a in processed if a.get("analysis")]

    col1.metric("Articles collected", len(articles))
    col2.metric("Articles analyzed", len(processed))
    col3.metric("Active themes", len(themes))
    col4.metric("Avg score", f"{sum(scores)/len(scores):.1f}/10" if scores else "-")

    if scores:
        st.subheader("Score distribution")
        df = pd.DataFrame({"score": scores})
        fig = px.histogram(df, x="score", nbins=10, range_x=[1, 10],
                           color_discrete_sequence=["#5865F2"])
        fig.update_layout(bargap=0.1, xaxis_title="Score", yaxis_title="Articles")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Latest analyzed articles")
    top = [a for a in processed if a.get("analysis")][:10]
    if top:
        for a in top:
            score = a["analysis"]["relevance_score"]
            color = "🟢" if score >= 7 else "🟡" if score >= 4 else "🔴"
            st.markdown(f"{color} **[{a['title']}]({a['url']})** - Score: `{score}/10`")
            st.caption(a["analysis"].get("summary", ""))
    else:
        st.info("No analyzed articles yet.")

except Exception as e:
    st.error(f"Could not reach the API: {e}")
    st.info("Make sure the backend is running.")