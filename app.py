import streamlit as st
from config.settings import Settings
from config.session import SessionManager
from _login.Login import login_page
from _dashboard.Dashboard import dashboard_page
from _clients.Clients import client_detail_page
from api.client import APIClient

def create_client_page_function(customer_data):
    """Creates a function that returns the client detail page with fixed customer data"""
    def page_function():
        return client_detail_page(customer_data)
    page_function.__name__ = f"client_{customer_data['id']}"
    return page_function

def main():
    st.set_page_config(
        page_title=Settings.PAGE_TITLE,
        page_icon=Settings.PAGE_ICON,
        layout="wide"
    )
    
    SessionManager.init_session()
    
    # Construct base pages
    login_Page = st.Page(login_page, title="Log in", icon=":material/login:")
    logout_Page = st.Page(SessionManager.clear_session, title="Log out", icon=":material/logout:")
    dashboard = st.Page(dashboard_page, title="Dashboard", icon=":material/dashboard:", default=True)
    
    # Dynamically create client detail pages
    client_pages = []
    if st.session_state.logged_in:
        api_client = APIClient.create_client(st.session_state.token)
        
        # Get customers once and store in session state if not already present
        if 'customers' not in st.session_state:
            st.session_state.customers = api_client.get_customers(per_page=-1)
        
        # Create pages from cached customer data
        for customer in st.session_state.customers:
            # Make a deep copy of the customer data
            customer_data = dict(customer)
            
            client_page = st.Page(
                create_client_page_function(customer_data),
                title=f"{customer_data['first_name']} {customer_data['last_name']}",
                icon=":material/people:",
                url_path=f"client_{customer_data['id']}"
            )
            client_pages.append(client_page)

    # Show navigation
    if st.session_state.logged_in:
        pg = st.navigation(
            {
                "Account": [logout_Page],
                "Dashboard": [dashboard],
                "Clients": client_pages
            }
        )
    else:
        pg = st.navigation([login_Page])

    pg.run()

if __name__ == "__main__":
    main()