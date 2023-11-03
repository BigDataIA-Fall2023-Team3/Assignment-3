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

# Function to display user details
def display_user_details(token):
    st.subheader("User Details")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("https://assignment-3-b24bd7fda897.herokuapp.com/users", headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        st.write(f"Username: {user_data['username']}")
        st.write(f"Email: {user_data['email']}")

# Function to update user profile
def update_user_profile(token):
    st.subheader("Update Profile")
    new_email = st.text_input("New Email")
    new_password = st.text_input("New Password", type="password")
    update_button = st.button("Update")

    if update_button:
        update_data = {
            "email": new_email,
            "new_password": new_password
        }
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.put("https://assignment-3-b24bd7fda897.herokuapp.com/users/update", json=update_data, headers=headers)
        if response.status_code == 200:
            st.success("Profile updated successfully!")
        else:
            st.error("Failed to update profile.")


# Initialize user_data as an empty dictionary
user_data = st.session_state.get("user_data", {})

# Sign-in section
st.sidebar.subheader("Sign In")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

sign_in_button = st.sidebar.button("Sign In")

if sign_in_button:
    token = get_jwt_token(username, password)
    if token:
        user_data = {
            "token": token,
            "signed_in": True
        }
        st.session_state.user_data = user_data
        st.success("Sign in successful!")
        st.title("Welcome to SEC Data Vector Search Platform!")
    else:
        st.sidebar.error("Sign in failed. Invalid credentials.")

# Check if signed in
if user_data.get("signed_in", False):
    # Display user details
    with st.expander("User Details"):
        display_user_details(user_data['token'])

    # Update Profile section
    with st.expander("Update Profile"):
        update_user_profile(user_data['token'])

    # Logout button
    logout_button = st.button("Logout")
    if logout_button:
        st.session_state.user_data = {}
        st.warning("Logged out successfully!")

# Clear session data if the user logs out
if not user_data.get("signed_in", False):
    st.session_state.user_data = {}
