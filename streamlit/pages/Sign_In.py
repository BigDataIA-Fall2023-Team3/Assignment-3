import streamlit as st
import requests

# Define a function to get the JWT token
def get_jwt_token(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = requests.post("https://assignment-3-b24bd7fda897.herokuapp.com/token", data=data)
    if response.status_code == 200:
        token = response.json().get("access_token")
        return token
    return None

# Initialize user_data as an empty dictionary
user_data = {}

# Sign-in section
st.sidebar.subheader("Sign In")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Sign In"):
    token = get_jwt_token(username, password)
    if token:
        st.success("Sign in successful!")
        user_data['token'] = token
    else:
        st.sidebar.error("Sign in failed. Invalid credentials.")

# Check if signed in
if 'token' in user_data:
    # Display user details
    st.subheader("User Details")
    headers = {"Authorization": f"Bearer {user_data['token']}"}
    response = requests.get("https://assignment-3-b24bd7fda897.herokuapp.com/users", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        st.write(f"Username: {user_data['username']}")
        st.write(f"Email: {user_data['email']}")

    # Update Profile section
    st.subheader("Update Profile")
    new_email = st.text_input("New Email", user_data.get('email', ''))
    new_password = st.text_input("New Password", type="password")
    if st.button("Update"):
        update_data = {
            "email": new_email,
            "new_password": new_password
        }
        headers = {"Authorization": f"Bearer {user_data['token']}"}
        response = requests.put("https://assignment-3-b24bd7fda897.herokuapp.com/users/update", json=update_data, headers=headers)
        if response.status_code == 200:
            st.success("Profile updated successfully!")
            # Update the user_data with new email
            user_data['email'] = new_email
        else:
            st.error("Failed to update profile.")
