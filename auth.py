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
    """Fetch and store user info from /me endpoint."""
    try:
        with httpx.Client() as client:
            resp = client.get(f"{API_URL}/auth/me", headers=get_headers())
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["user_email"] = data["email"]
            st.session_state["totp_enabled"] = data["totp_enabled"]
    except Exception:
        pass


def logout():
    refresh_token = st.session_state.get("refresh_token", "")
    if refresh_token:
        try:
            with httpx.Client() as client:
                client.post(
                    f"{API_URL}/auth/logout",
                    json={"refresh_token": refresh_token},
                    headers=get_headers()
                )
        except Exception:
            pass
    for key in ["access_token", "refresh_token", "user_email", "totp_enabled"]:
        st.session_state.pop(key, None)
    st.rerun()


def refresh_access_token() -> bool:
    refresh_token = st.session_state.get("refresh_token", "")
    if not refresh_token:
        return False
    try:
        with httpx.Client() as client:
            resp = client.post(
                f"{API_URL}/auth/refresh",
                json={"refresh_token": refresh_token}
            )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["access_token"] = data["access_token"]
            st.session_state["refresh_token"] = data["refresh_token"]
            return True
    except Exception:
        pass
    return False