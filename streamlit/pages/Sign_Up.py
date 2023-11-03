import streamlit as st
import requests
import time

st.title('Sign Up')

with st.form(key='sign_up_form'):
    username = st.text_input(label='Username')
    email = st.text_input(label='Email')
    password = st.text_input(label='Password', type='password')
    submit_button = st.form_submit_button(label='Sign Up')

    if submit_button:
        api_url = 'https://assignment-3-ec7a8fd53eb5.herokuapp.com/register'
        payload = {
            'username': username,
            'email': email,
            'password': password
        }

        try:
            response = requests.post(api_url, json=payload)
            if response.status_code == 200:
                st.success('User created successfully!')
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")


