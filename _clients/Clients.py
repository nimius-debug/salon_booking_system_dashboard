import streamlit as st
import pandas as pd
from api.client import APIClient
from datetime import datetime, timedelta


@st.dialog("Edit Admin Note", width='large')
def edit_note_dialog(booking, api_client):
    """Dialog for editing admin notes"""
    current_note = booking.get('admin_note', '')
    st.text_area(
        "Admin Note", 
        value=current_note,
        key="new_note",
        height=300,
        placeholder="Enter admin note here..."
    )
    
    if st.button("Save"):
        with st.spinner("Updating note..."):
            update_data = {
                "id": booking['id'],
                "date": booking['date'],
                "time": booking['time'],
                "status": booking['status'],
                "admin_note": st.session_state.new_note
            }
            
            if api_client.update_booking(booking['id'], update_data):
                st.session_state.note_updated = True
                api_client.get_bookings.clear()
                st.rerun()
            else:
                st.error("Failed to update note")


def client_detail_page(customer_data):
    st.header(f"{customer_data['first_name']} {customer_data['last_name']}")
    
    # Create columns for customer information
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Contact Information**")
        st.write(f"📧 Email: {customer_data['email']}")
        st.write(f"📞 Phone: {customer_data['phone']}")
        st.write(f"📍 Address: {customer_data['address']}")
    
    with col2:
        st.write("**Notes**")
        st.text_area("Customer Notes", value=customer_data['note'], disabled=True)
    
    # Add booking history section
    st.subheader("Booking History")
    api_client = APIClient.create_client(st.session_state.token)
    
    # Fetch customer's bookings with date_time sorting
    bookings = api_client.get_bookings(
        customers=[customer_data['id']],
        start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        end_date=datetime.now().strftime("%Y-%m-%d"),
        orderby="date_time",
        order="desc"
    )

    if bookings:
        for booking in bookings:
            service = booking['services'][0] if booking.get('services') else None
            
            if service:
                booking_date = pd.to_datetime(booking['date']).strftime('%d/%b/%Y')
                service_name = service.get('service_name', 'Unknown Service')
                status = booking['status'].replace('sln-b-', '').title() if booking.get('status') else ''
                expander_title = f"📆 {booking_date} - {service_name} ({status})"
                
                with st.expander(expander_title, expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Service Details:**")
                        st.write(f"⏰ Time: {service.get('start_at', 'N/A')}")
                        st.write(f"⌛ Duration: {booking.get('duration', 'N/A')}")
                    
                    with col2:
                        st.write("**Payment Details:**")
                        st.write(f"💵 Cost: ${service.get('service_price', 0):,.2f}")
                        st.write(f"💰 Total Amount: ${booking.get('amount', 0):,.2f}")
                    
                    # Admin Notes Section with Dialog
                    st.write("**Admin Notes:**")
                    if booking.get('admin_note'):
                        st.info(booking['admin_note'])
                    
                    if st.button("✏️ Edit Note", key=f"edit_note_{booking['id']}"):
                        edit_note_dialog(booking, api_client)
                    
                    # Show success message if note was updated
                    if st.session_state.get('note_updated'):
                        st.toast("Note updated successfully!")
                        del st.session_state.note_updated
                    
    else:
        st.info("No booking history found")