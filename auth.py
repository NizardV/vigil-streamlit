import streamlit as st
import httpx
import os

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")


def get_session_id() -> str | None:
    """Récupère le session_id depuis le header nginx X-Session-ID."""
    return st.context.headers.get("X-Session-Id")


def is_authenticated() -> bool:
    return bool(get_session_id())


def get_cookies() -> dict:
    """Retourne le cookie de session pour les appels httpX."""
    session_id = get_session_id()
    if not session_id:
        return {}
    return {"vigil_session_id": session_id}


def get_headers() -> dict:
    """Gardé pour compatibilité — n'envoie plus de Bearer token."""
    return {}


def fetch_user_info():
    try:
        with httpx.Client() as client:
            resp = client.get(
                f"{API_URL}/auth/me",
                cookies=get_cookies()
            )
        if resp.status_code == 200:
            data = resp.json()
            st.session_state["user_email"] = data["email"]
            st.session_state["totp_enabled"] = data["totp_enabled"]
    except Exception:
        pass