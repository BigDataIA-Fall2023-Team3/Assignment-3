# pages/sign_in.py
import streamlit as st
import requests

# Function to make a POST request to the FastAPI /token endpoint
def get_token(username, password):
    response = requests.post('http://localhost:8000/token', data={'username': username, 'password': password})
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        return None

def app():
    st.title('Sign In')

    # Creating a form for user input
    with st.form(key='sign_in_form'):
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')
        submit_button = st.form_submit_button(label='Sign In')

        # When the form is submitted, attempt to authenticate the user
        if submit_button:
            token = get_token(username, password)
            if token:
                st.success('You have successfully logged in!')
                # You can then use the token to make authenticated requests to your backend
                st.session_state['token'] = token
                # Redirect to another page, or display the chatbot, etc.
            else:
                st.error('Login failed. Check your username and/or password.')
