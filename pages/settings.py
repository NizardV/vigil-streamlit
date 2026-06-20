import streamlit as st
import httpx
import os
from auth import get_headers, fetch_user_info

API_URL = os.getenv("API_URL", "http://vigil_backend:8000/api")

st.title("Settings")

totp_enabled = st.session_state.get("totp_enabled", False)

# ── TOTP Section ─────────────────────────────────────────
st.subheader("Two-Factor Authentication (TOTP)")

if totp_enabled:
    st.success("✅ TOTP is enabled on your account.")
    st.caption("You will be asked for a code from your authenticator app at each login.")

    with st.form("disable_totp"):
        st.warning("To disable TOTP, enter a valid code from your authenticator app.")
        code = st.text_input("Authentication code", max_chars=6, placeholder="000000")
        submitted = st.form_submit_button("Disable TOTP", use_container_width=True)

    if submitted:
        if not code:
            st.error("Please enter your authentication code.")
        else:
            try:
                with httpx.Client() as client:
                    resp = client.post(
                        f"{API_URL}/auth/totp/disable",
                        json={"code": code},
                        headers=get_headers()
                    )
                if resp.status_code == 200:
                    fetch_user_info()
                    st.success("TOTP disabled successfully.")
                    st.rerun()
                else:
                    st.error("Invalid code. Please try again.")
            except Exception as e:
                st.error(f"Connection error: {e}")
else:
    st.info("TOTP is not enabled. Add an extra layer of security to your account.")

    if st.button("Set up TOTP", use_container_width=True):
        try:
            with httpx.Client() as client:
                resp = client.post(f"{API_URL}/auth/totp/setup", headers=get_headers())
            if resp.status_code == 200:
                data = resp.json()
                st.session_state["totp_setup_secret"] = data["secret"]
                st.session_state["totp_setup_qr"] = data["qr_code"]
        except Exception as e:
            st.error(f"Connection error: {e}")

    if st.session_state.get("totp_setup_secret"):
        st.divider()
        st.markdown("**1. Scan this QR code with your authenticator app**")
        st.image(
            f"data:image/png;base64,{st.session_state['totp_setup_qr']}",
            width=200
        )
        st.caption(f"Or enter this code manually: `{st.session_state['totp_setup_secret']}`")

        st.markdown("**2. Enter the 6-digit code to confirm**")
        with st.form("enable_totp"):
            code = st.text_input("Authentication code", max_chars=6, placeholder="000000")
            submitted = st.form_submit_button("Enable TOTP", use_container_width=True)

        if submitted:
            if not code:
                st.error("Please enter the code.")
            else:
                try:
                    with httpx.Client() as client:
                        resp = client.post(
                            f"{API_URL}/auth/totp/enable",
                            json={
                                "secret": st.session_state["totp_setup_secret"],
                                "code": code
                            },
                            headers=get_headers()
                        )
                    if resp.status_code == 200:
                        st.session_state.pop("totp_setup_secret", None)
                        st.session_state.pop("totp_setup_qr", None)
                        fetch_user_info()
                        st.success("TOTP enabled successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid code. Please try again.")
                except Exception as e:
                    st.error(f"Connection error: {e}")