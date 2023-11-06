import streamlit as st
import requests

def app():
    st.title('Sign Up')

    with st.form(key='sign_up_form'):
        username = st.text_input(label='Username')
        email = st.text_input(label='Email')
        password = st.text_input(label='Password', type='password')
        submit_button = st.form_submit_button(label='Sign Up')

        if submit_button:
            response = requests.post('http://localhost:8000/register', json={
                'username': username,
                'email': email,
                'password': password
            })

            if response.status_code == 200:
                st.success('User created successfully! Please go to Sign In.')
            else:
                st.error('Error: %s' % response.json()['detail'])
