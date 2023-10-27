import streamlit as st
import streamlit.pages.database as db
st.subheader("Create New Account")
new_user = st.text_input("Username")
new_password = st.text_input("Password", type='password')
new_email = st.text_input("Email")

if st.sidebar.button("Signup"):
    # Send a POST request to your FastAPI /register endpoint to register a new user
    signup_data = {
        "username": new_user,
        "email": new_email,
        "password": new_password
    }
    response = requests.post(f"{https://assignment-3-cdda932ac280.herokuapp.com}/register", data=signup_data)
    
    if response.status_code == 200:
        st.success("You have successfully created an account")
    else:
        st.warning("Username already exists. Choose a different one.")
