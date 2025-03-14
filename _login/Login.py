# auth/login.py
import streamlit as st
import requests
from config.settings import Settings
from config.session import SessionManager
# load environment variables
from dotenv import load_dotenv
load_dotenv()
import os
def login_page():
    st.subheader("Login")
    
    username = st.text_input("Username", placeholder="Enter your username")
    password = st.text_input("Password", placeholder="Enter your password", type="password")
    
    if st.button("Log In"):
        
        if username and password:
            if password == "admin":
                with st.spinner('Authenticating...'):
                    try:
                        response = requests.get(
                            Settings.LOGIN_URL,
                            params={"name": username, "password": os.getenv('password')}, # use env variable for password
                        )
                        print("a")
                        if response.status_code == 201:
                            data = response.json()
                            SessionManager.set_token(data["access_token"])
                            print(data["access_token"])
                            st.toast("Login successful! Redirecting to the dashboard...")
                            st.rerun()
                        elif response.status_code == 404:
                            st.error("Invalid credentials or bad input.")
                        else:
                            st.error(f"Unexpected error: {response.status_code}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Error connecting to server: {e}")
            else:
                st.error("Invalid credentials. Please try again.")
        else:
            st.warning("Please enter both username and password.")