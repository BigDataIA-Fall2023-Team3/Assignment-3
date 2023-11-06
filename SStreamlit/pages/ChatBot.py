import streamlit as st
import requests
import json

# Function to handle new message submissions


import json
import requests
import streamlit as st

def handle_new_message(question, file, api_key, token):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    data = {
        "query_model": {
            "query": question,
            "filename": file
        },
        "openai_model": {
            "api_key": api_key
        }
    }
    
    try:
        response = requests.post(
            'https://assignment-3-ec7a8fd53eb5.herokuapp.com/answer/',
            headers=headers, json=data
        )
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        # Check if the response is in JSON format
        if response.headers.get('Content-Type') == 'application/json':
            answer_data = response.json()
        else:
            # If not, print the response or handle it as a raw string
            answer_data = response.text
            print("Response is not in JSON format:", answer_data)
            return None

        # Now you can safely use .get() on answer_data, since it's expected to be a dictionary
        answer = answer_data.get('answer', 'No answer returned')
        return answer

    except requests.exceptions.RequestException as e:
        st.error(f'Request failed: {e}')
        return 'Request failed: {}'.format(e)
    except Exception as e:
        st.error(f'An unexpected error occurred: {e}')
        return 'An unexpected error occurred: {}'.format(e)


        

# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

st.sidebar.subheader("Sign In")
username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

sign_in_button = st.sidebar.button("Sign In")

if sign_in_button:
    try:
        response = requests.post(
            'https://assignment-3-ec7a8fd53eb5.herokuapp.com/token',
            data={
                'username': username,
                'password': password
            }
        )

        if response.status_code == 200:
            token = response.json().get('access_token', None)
            if token:
                st.session_state['access_token'] = token
                st.success('You are successfully signed in!')
            else:
                st.error('Received status code 200 but no token was found in the response.')
        else:
            st.error('Login failed. Check your username and/or password.')
    except requests.exceptions.RequestException as e:
        st.error(f'An error occurred: {e}')
    except Exception as e:
        st.error(f'An unexpected error occurred: {e}')



st.title('Chatbot')

# Only show chatbot to signed-in users
if st.session_state.get('access_token'):
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {st.session_state["access_token"]}'
    }
    
    # Retrieve and display user details
    try:
        response = requests.get('https://assignment-3-ec7a8fd53eb5.herokuapp.com/users', headers=headers)
        response.raise_for_status()
        user_details = response.json()
        st.subheader(f"Welcome {user_details['username']}!")
        st.text(f"Email: {user_details['email']}")
        if user_details['logs']:
            st.text(f"Logs: {user_details['logs']}")
        else:
            st.text('No logs available.')
    except requests.exceptions.RequestException as e:
        st.error(f'Request failed: {e}')
    except Exception as e:
        st.error(f'An unexpected error occurred: {e}')



    # Input for new questions
with st.form("chat_form"):
    question = st.text_input('Ask a question', key='question')
    file = st.text_input('File', key='file')
    openai_key = st.text_input('OpenAI Key', key='openai_key')
    submit_button = st.form_submit_button(label='Submit')

if submit_button and question and st.session_state.get('access_token') and file and openai_key:
    # Call the message handler function and pass the token from session_state
    answer_data = handle_new_message(question, file, openai_key, st.session_state['access_token'])
    if answer_data and isinstance(answer_data, dict):
        # Update chat history with the new question and answer
        st.session_state['chat_history'].append({
            'question': question,
            'answer': answer_data.get('answer', 'No answer returned')
        })

# Display chat history
for chat in st.session_state['chat_history']:
    st.text_area(f"Q: {chat['question']}", value=chat['answer'], height=75, disabled=True)

else:
    st.warning('Please sign in to use the chatbot.')



