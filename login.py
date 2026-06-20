import streamlit as st
import httpx
import os
from auth import fetch_user_info
from streamlit_cookies_controller import CookieController

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

cookie = CookieController()

# ── TOTP step ────────────────────────────────────────────
if st.session_state.get("totp_temp_token"):
    st.title("Two-Factor Authentication")
    st.info("Enter the 6-digit code from your authenticator app.")

    with st.form("totp_form"):
        code = st.text_input("Authentication code", max_chars=6, placeholder="000000")
        submitted = st.form_submit_button("Verify", use_container_width=True)

    if submitted:
        if not code:
            st.error("Please enter your authentication code.")
        else:
            try:
                with httpx.Client() as client:
                    resp = client.post(f"{API_URL}/auth/totp/verify", json={
                        "temp_token": st.session_state["totp_temp_token"],
                        "code": code
                    })
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state["access_token"] = data["access_token"]
                    st.session_state["refresh_token"] = data["refresh_token"]
                    st.session_state.pop("totp_temp_token", None)
                    cookie.set("vigil_refresh_token", data["refresh_token"], max_age=30*24*60*60)
                    fetch_user_info()
                    st.rerun()
                else:
                    st.error("Invalid authentication code. Please try again.")
            except Exception as e:
                st.error(f"Connection error: {e}")

    if st.button("← Back to login"):
        st.session_state.pop("totp_temp_token", None)
        st.rerun()

    st.stop()

# ── Login / Register tabs ────────────────────────────────
st.title("Welcome to Vigil")
st.caption("Automated tech watch system")

if st.session_state.get("register_success"):
    st.success("Account created! Please check your email to confirm your account.")
    st.session_state.pop("register_success", None)

tab_login, tab_register = st.tabs(["Login", "Create account"])

with tab_login:
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", use_container_width=True)

    if submitted:
        if not email or not password:
            st.error("Please fill in all fields.")
        else:
            try:
                with httpx.Client() as client:
                    resp = client.post(f"{API_URL}/auth/login", json={
                        "email": email,
                        "password": password
                    })
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("requires_totp"):
                        st.session_state["totp_temp_token"] = data["temp_token"]
                        st.rerun()
                    else:
                        st.session_state["access_token"] = data["access_token"]
                        st.session_state["refresh_token"] = data["refresh_token"]
                        cookie.set("vigil_refresh_token", data["refresh_token"], max_age=30*24*60*60)
                        fetch_user_info()
                        st.rerun()
                elif resp.status_code == 403:
                    detail = resp.json().get("detail", "")
                    if "verify" in detail.lower():
                        st.warning("Please verify your email before logging in. Check your inbox.")
                    else:
                        st.error(detail)
                else:
                    st.error("Invalid email or password.")
            except Exception as e:
                st.error(f"Connection error: {e}")

with tab_register:
    with st.form("register_form"):
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_password2 = st.text_input("Confirm password", type="password", key="reg_password2")
        submitted_reg = st.form_submit_button("Create account", use_container_width=True)

    if submitted_reg:
        if not reg_email or not reg_password or not reg_password2:
            st.error("Please fill in all fields.")
        elif reg_password != reg_password2:
            st.error("Passwords do not match.")
        elif len(reg_password) < 8:
            st.error("Password must be at least 8 characters.")
        else:
            try:
                with httpx.Client() as client:
                    resp = client.post(f"{API_URL}/auth/register", json={
                        "email": reg_email,
                        "password": reg_password
                    })
                if resp.status_code == 201:
                    st.session_state["register_success"] = True
                    st.rerun()
                elif resp.status_code == 409:
                    st.error("This email is already registered.")
                else:
                    st.error("An error occurred. Please try again.")
            except Exception as e:
                st.error(f"Connection error: {e}")