# pages/dashboard.py
import streamlit as st
from api.client import APIClient

def dashboard_page():
    st.subheader("Dashboard")
    st.write("Welcome to the dashboard!")
    
    api_client = APIClient(st.session_state.token)
    response = api_client.get_customers()
    
    if response.status_code == 200:
        customers = response.json().get("items", [])
        customer_names = [
            f"{c['first_name']} {c['last_name']} (ID: {c['id']})"
            for c in customers
        ]

        selected_customer = st.selectbox("Select a Customer", customer_names)
        
        if selected_customer:
            customer_id = customers[customer_names.index(selected_customer)]["id"]
            customer_details = customers[customer_names.index(selected_customer)]

            st.write("### Customer Details")
            st.json(customer_details)

            if customer_details["bookings"]:
                st.write("### Bookings")
                for booking_id in customer_details["bookings"]:
                    st.write(f"Booking ID: {booking_id}")
            else:
                st.write("No bookings available for this customer.")
    elif response.status_code == 404:
        st.error("No customers found.")
    else:
        st.error(f"Unexpected error: {response.status_code}")