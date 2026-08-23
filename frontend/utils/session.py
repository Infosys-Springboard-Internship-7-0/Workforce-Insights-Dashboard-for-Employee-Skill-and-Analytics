import streamlit as st


def is_authenticated():
    return bool(st.session_state.get("token"))


def is_admin():
    user = st.session_state.get("user")
    return bool(user and user.get("role") == "admin")


def clear_session():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.messages = []
