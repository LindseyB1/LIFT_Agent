import streamlit as st


def render_header(app_title, subtitle):
    st.title(app_title)
    st.caption(subtitle)


def render_welcome_panel():
    with st.expander("Welcome / How to Use", expanded=False):
        st.markdown(
            """
1. Enter a public or synthetic request.
2. Choose the desired output style.
3. Generate the response.
4. Review the LLM route decision and tool trace.
5. Save an evaluation record.
"""
        )


def render_safety_notice():
    st.info(
        "Use public or synthetic information only. Do not enter private, classified, restricted, protected, or sensitive information."
    )
