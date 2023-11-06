# pages/chatbot.py
import streamlit as st
import requests

def send_query(query, token):
    # You should include the user's token in the header to authenticate the request.
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post('http://localhost:8000/answer/', headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        return None

def app():
    st.title('Chat with Bot')

    # This assumes that the user's token is stored in the session state.
    token = st.session_state.get('token', '')

    if not token:
        st.warning("You need to sign in first.")
        st.stop()

    # Chatbot interaction form
    with st.form(key='chatbot_query_form'):
        query = st.text_area('Ask a question:', help='Type your question for the chatbot here.')
        submit_button = st.form_submit_button(label='Submit')

        if submit_button and query:
            response = send_query(query, token)
            if response:
                st.success('Here is the response from the chatbot:')
                st.write(response)
            else:
                st.error('An error occurred. Please try again later.')

