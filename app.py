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
    
    # Construct pages
    login_Page = st.Page(login_page, title="Log in", icon=":material/login:")
    logout_Page = st.Page(SessionManager.clear_session, title="Log out", icon=":material/logout:")

    dashboard = st.Page(
        dashboard_page, title="Dashboard", icon=":material/dashboard:", default=True
    )

    

    # Show navigation
    if st.session_state.logged_in:
        pg = st.navigation(
            {
                "Account": [logout_Page],
                "Dashboard": [dashboard],
            }
        )
    else:
        pg = st.navigation([login_Page])

    #debugging
    #st.write(st.session_state)  # for debugging
    pg.run()

if __name__ == "__main__":
    main()