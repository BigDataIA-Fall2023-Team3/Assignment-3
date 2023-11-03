import streamlit as st
import requests


signup_successful = False  # Flag to track if sign-up was successful

if not signup_successful:
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
    print(response)

    # Print the response content and status code for debugging
    st.write(f"Response Content: {response.content}")
    st.write(f"Response Status Code: {response.status_code}")

    # Check the response status code and handle it accordingly
    if response.status_code == 200:
        st.success("User registered successfully!")
        signup_successful = True  # Set the flag to True

    elif response.status_code == 400:
        st.error("Registration failed. Username or email already exists.")
    elif response.status_code == 401:
        st.error("Registration failed. Email already exists.")
    elif response.status_code == 402:
        st.error("Registration failed. Invalid email format.")
    else:
        st.error("Registration failed. Please try again later.")

# Conditionally display a welcome message after successful sign-up
if signup_successful:
    st.title("Welcome to SEC Data Vector Search Platform!")
    st.write("""
        Login to your account to start exploring!
        """)
