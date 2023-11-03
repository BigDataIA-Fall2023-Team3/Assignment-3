import streamlit as st
import requests

st.subheader("Create New Account")
new_user = st.text_input("Username")
new_password = st.text_input("Password", type='password')
new_email = st.text_input("Email")

if st.sidebar.button("Signup"):
    # Prepare the signup data as a dictionary
    signup_data = {
        "username": new_user,
        "email": new_email,
        "password": new_password
    }

    # Send a POST request to your FastAPI /register endpoint
    response = requests.post("https://assignment-3-b24bd7fda897.herokuapp.com/register", json=signup_data)

    # Check the response status code
    if response.status_code == 200:
        st.success("User registered successfully!")
    elif response.status_code == 400:
        st.error("Registration failed. Username or email already exists.")
    elif response.status_code == 401:
        st.error("Registration failed. Email already exists.")
    elif response.status_code == 402:
        st.error("Registration failed. Invalid email format.")
    else:
        st.error("Registration failed. Please try again later.")
