import os
import streamlit as st


def auth_required():
    value = ""
    try:
        value = st.secrets.get("P3_AUTH_REQUIRED", "")
    except Exception:
        value = ""

    if not value:
        value = os.getenv("P3_AUTH_REQUIRED", "false")

    return str(value).strip().lower() in {"1", "true", "yes", "required"}


def render_auth_gate():
    """
    Demo-safe authentication gate.

    Default:
    - Demo mode is open so an instructor can grade the app.

    Production:
    - Set P3_AUTH_REQUIRED=true to display the authentication notice.
    - Real authentication should be handled through Streamlit/identity-provider setup.
    """
    with st.sidebar:
        st.subheader("Access Mode")

        if auth_required():
            st.warning("Authentication required mode is enabled.")
            st.caption(
                "Configure Streamlit authentication or an external identity provider for production."
            )
        else:
            st.success("Demo mode")
            st.caption("Open for grading and testing. Do not enter sensitive data.")
