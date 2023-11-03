import streamlit as st


import requests

st.title("Welcome to SEC Data Vector Search Platform!")

st.sidebar.subheader("Enter Login Details")

username = st.sidebar.text_input("User Name")
password = st.sidebar.text_input("Password", type='password')

if st.sidebar.button("Login"):
    # Send a POST request to your FastAPI /token endpoint to authenticate the user
    login_data = {
        "username": username,
        "password": password
    }
    response = requests.post(f"{https://assignment-3-cdda932ac280.herokuapp.com}/token", data=login_data)
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        st.success("Logged in Successfully")
        st.write("Welcome, ", username)
        st.write(f"Access Token: {access_token}")
    else:
        st.warning("Incorrect Username/Password")