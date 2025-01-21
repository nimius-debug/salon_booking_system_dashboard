# main.py
import streamlit as st
from config.settings import Settings
from config.session import SessionManager
from _login.Login import login_page
from _dashboard.Dashboard import dashboard_page
def main():
    st.set_page_config(
        page_title=Settings.PAGE_TITLE,
        page_icon=Settings.PAGE_ICON,
        layout="wide"
    )
    
    SessionManager.init_session()
    
    if not st.session_state.logged_in:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()