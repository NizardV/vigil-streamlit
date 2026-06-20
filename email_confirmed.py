import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.title("Email Confirmation")

# Get token from URL query params
params = st.query_params
token = params.get("token")

if not token:
    st.error("Invalid confirmation link.")
    st.stop()

# Call the API to verify the token
try:
    with httpx.Client() as client:
        resp = client.get(f"{API_URL}/auth/verify/{token}")

    if resp.status_code == 200:
        st.success("✅ Email confirmed! Your account is now active.")
        st.info("You can now log in to Vigil.")
        if st.button("Go to Login →", use_container_width=True):
            st.switch_page("login.py")
    elif resp.status_code == 400:
        detail = resp.json().get("detail", "")
        if "expired" in detail.lower():
            st.error("This confirmation link has expired. Please register again.")
        else:
            st.error("This confirmation link is invalid or has already been used.")
    else:
        st.error("An error occurred. Please try again.")

except Exception as e:
    st.error(f"Connection error: {e}")