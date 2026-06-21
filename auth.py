import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")


def is_authenticated() -> bool:
    return bool(st.session_state.get("access_token"))


def get_headers() -> dict:
    token = st.session_state.get("access_token", "")
    return {"Authorization": f"Bearer {token}"}


def fetch_user_info():
    try:
        with httpx.Client() as client:
            resp = client.get(f"{API_URL}/auth/me", headers=get_headers())
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["user_email"] = data["email"]
            st.session_state["totp_enabled"] = data["totp_enabled"]
    except Exception:
        pass


def restore_session(session_id: str) -> bool:
    try:
        with httpx.Client() as client:
            resp = client.get(f"{API_URL}/auth/session/{session_id}")
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["access_token"] = data["access_token"]
            st.session_state["refresh_token"] = data["refresh_token"]
            return True
    except Exception:
        pass
    return False