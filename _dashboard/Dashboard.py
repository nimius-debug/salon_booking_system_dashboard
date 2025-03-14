# pages/dashboard.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from api.client import APIClient

def format_currency(amount):
    return f"${amount:,.2f}"

def dashboard_page():
    st.title("Dashboard")

    # ===== FILTERS ON MAIN PAGE =====
    st.subheader("Filters")
    
    # Time period selection
    time_period = st.radio(
        "Time Period",
        ["Week", "Month", "All Time", "Custom"],
        index=1,
        horizontal=True,
    )

    # Define default end_date as today
    end_date = datetime.today()

    # Determine start_date and end_date based on time_period
    if time_period == "Custom":
        start_date = st.date_input("Start Date", end_date - timedelta(days=30))
        end_date = st.date_input("End Date", end_date)
    else:
        if time_period == "Week":
            start_date = end_date - timedelta(days=7)
        elif time_period == "Month":
            start_date = end_date - timedelta(days=30)
        else:  # All Time
            start_date = end_date - timedelta(days=365*5)  # 5 years back

    # Slider for upcoming bookings
    upcoming_hours = st.slider("Show upcoming bookings (hours)", 1, 3600, 24)

    # ===== DATA LOADING =====
    with st.spinner("Loading business insights..."):
        # Initialize API client
        api_client = APIClient.create_client(st.session_state.token)

        # Fetch data
        bookings = api_client.get_bookings(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        upcoming = api_client.get_upcoming_bookings(hours=upcoming_hours)
        customers = api_client.get_customers()

    # ===== TOP METRICS =====
    st.header("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Clients", len(customers))
    
    with col2:
        st.metric("Total Bookings", len(bookings))
    
    with col3:
        total_revenue = sum(b['amount'] for b in bookings) if bookings else 0
        st.metric("Total Revenue", format_currency(total_revenue))
    
    with col4:
        st.metric("Upcoming", len(upcoming))

    # ===== BOOKINGS CHART =====
    st.header("Bookings Overview")
    if bookings:
        bookings_df = pd.DataFrame(bookings)
        bookings_df["date"] = pd.to_datetime(bookings_df["date"])
        
        # Group by day (daily frequency)
        daily_bookings = bookings_df.set_index("date").resample('D').size()
        daily_bookings.name = "Bookings"

        # Simple chart: days on x-axis, booking counts on y-axis
        st.line_chart(daily_bookings)  # You can also use st.bar_chart if you prefer bars
    else:
        st.info("No bookings data available")

    # ===== UPCOMING BOOKINGS =====
    st.header(f"Upcoming Appointments (Next {upcoming_hours} hours)")

    if upcoming:
        # Fetch all services in one go
        with st.spinner("Loading service details..."):
            try:
                services_dict = api_client.get_services()  # This now returns ID->name mapping
            except Exception as e:
                st.error(f"Error loading services: {str(e)}")
                services_dict = {}

        # Process each booking
        for booking in upcoming:
            # Convert to datetime
            booking_time = datetime.strptime(f"{booking['date']} {booking['time']}", "%Y-%m-%d %H:%M")
            
            with st.expander(
                f"{booking_time.strftime('%a, %b %d %I:%M %p')} - "
                f"{booking['customer_first_name']} {booking['customer_last_name']} "
                f"({booking['status'].replace('sln-b-', '').title()})",
                expanded=False
            ):
                # Two-column layout
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**Customer Information**")
                    st.write(f"📞 {booking.get('customer_phone', 'No phone')}")
                    st.write(f"📧 {booking.get('customer_email', 'No email')}")
                    st.write(f"🏠 {booking.get('customer_address', 'No address')}")
                    
                with col2:
                    st.markdown("**Appointment Details**")
                    st.write(f"🗓️ {booking_time.strftime('%B %d, %Y')}")
                    st.write(f"⏱️ Duration: {booking.get('duration', 'N/A')}")
                    st.write(f"💵 Total: {format_currency(booking.get('amount', 0))}")
                    st.write(f"🏪 Shop: {booking.get('shop', {}).get('title', 'N/A')}")

                # Display services with details
                if booking.get('services'):
                    st.markdown("**Booked Services**")
                    seen_services = set()  # Track displayed services to avoid duplicates
                    
                    for service in booking['services']:
                        service_id = str(service.get('service_id'))
                        service_name = services_dict.get(int(service_id), "Unknown Service")
                        
                        if service_id not in seen_services:
                            # Service information panel
                            with st.container():
                                cols = st.columns([4, 1])
                                with cols[0]:
                                    st.markdown(f"**{service_name}**")
                                with cols[1]:
                                    st.caption(f"ID: {service_id}")
                            seen_services.add(service_id)

                # Show booking notes
                if booking.get('note'):
                    st.markdown("**Booking Notes**")
                    st.info(booking['note'])

    else:
        st.info("No upcoming appointments in the selected time frame")

    # # ===== RECENT SERVICES =====
    # st.header("Recent Bookings Services")
    # if bookings:
    #     # Extract services from recent bookings
    #     services_list = []
    #     for booking in bookings:
    #         if 'services' in booking and booking['services']:
    #             for service in booking['services']:
    #                 services_list.append({
    #                     "Service Date": booking['date'],
    #                     "Service Name": service.get('name', 'N/A'),
    #                     "Duration": service.get('duration', 'N/A'),
    #                     "Price": service.get('price', 0)
    #                 })
        
    #     if services_list:
    #         services_df = pd.DataFrame(services_list)
    #         st.dataframe(
    #             services_df.sort_values("Service Date", ascending=False).head(5),
    #             column_config={
    #                 "Service Date": "Date",
    #                 "Service Name": "Service",
    #                 "Duration": "Duration",
    #                 "Price": "Price"
    #             },
    #             hide_index=True,
    #             use_container_width=True
    #         )
    #     else:
    #         st.info("No services found in recent bookings")
    # else:
    #     st.info("No bookings available to show services")


if __name__ == "__main__":
    dashboard_page()
