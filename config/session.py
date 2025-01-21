import streamlit as st

class SessionManager:
    @staticmethod
    def init_session():
        if "token" not in st.session_state:
            st.session_state.token = None
        if "logged_in" not in st.session_state:
            st.session_state.logged_in = False

    @staticmethod
    def set_token(token):
        st.session_state.token = token
        st.session_state.logged_in = True

    @staticmethod
    def clear_session():
        st.session_state.token = None
        st.session_state.logged_in = False
        st.rerun()
