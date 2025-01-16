import streamlit as st
import requests

LOGIN_URL  = 'https://skinbylauralo.com/wp-json/salon/api/v1/login'
CUSTOMERS_URL = 'https://skinbylauralo.com/wp-json/salon/api/v1/customers'
# Session state for storing the token
if "token" not in st.session_state:
    st.session_state["token"] = None

# Login Page
if not st.session_state["token"]:
    st.subheader("Login")

    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")

    if st.button("Log In"):
        if username and password:
            try:
                # API request to login
                response = requests.get(LOGIN_URL, params={"name": username, "password": password})
                
                if response.status_code == 201:
                    data = response.json()
                    st.session_state["token"] = data["access_token"]
                    st.success("Login successful! Redirecting to the dashboard...")
                elif response.status_code == 404:
                    st.error("Invalid credentials or bad input.")
                else:
                    st.error(f"Unexpected error: {response.status_code}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to server: {e}")
        else:
            st.warning("Please enter both username and password.")
else:
    # Dashboard Page
    st.subheader("Dashboard")
    st.write("Welcome to the dashboard!")

    # Fetch customers
    headers = {"Access-Token": st.session_state["token"]}
    params = {
        "search": "",
        "search_type": "contains",
        "search_field": "all",
        "orderby": "first_name_last_name",
        "order": "asc",
        "per_page": -1,
        "page": -1
    }

    response = requests.get(CUSTOMERS_URL, headers=headers, params=params)
    if response.status_code == 200:
        customers = response.json().get("items", [])
        customer_names = [f"{c['first_name']} {c['last_name']} (ID: {c['id']})" for c in customers]

        selected_customer = st.selectbox("Select a Customer", customer_names)
        
        if selected_customer:
            customer_id = customers[customer_names.index(selected_customer)]["id"]
            customer_details = customers[customer_names.index(selected_customer)]

            st.write("### Customer Details")
            st.json(customer_details)

            # Show bookings if available
            if customer_details["bookings"]:
                st.write("### Bookings")
                for booking_id in customer_details["bookings"]:
                    st.write(f"Booking ID: {booking_id}")
                    # You can make another API call to fetch booking details if needed
            else:
                st.write("No bookings available for this customer.")
    elif response.status_code == 404:
        st.error("No customers found.")
    else:
        st.error(f"Unexpected error: {response.status_code}")