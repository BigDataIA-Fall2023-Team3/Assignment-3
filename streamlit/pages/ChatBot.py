import requests
import streamlit as st
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import uuid
import logging
import pandas as pd
import time
import numpy as np
import os


import psycopg2

RDS_HOST = st.secrets['RDS_HOST']
RDS_PORT = st.secrets['RDS_PORT']
RDS_DB_NAME = st.secrets['RDS_DB_NAME']
RDS_USER = st.secrets['RDS_USER']
RDS_PASSWORD = st.secrets['RDS_PASSWORD']
DATABASE_URL = f"dbname='{RDS_DB_NAME}' user='{RDS_USER}' host='{RDS_HOST}' port={RDS_PORT} password='{RDS_PASSWORD}'"
# psql --host=assignment-3.cg4vo6ofeasg.us-east-1.rds.amazonaws.com --port=5432 --username=postgres --password --dbname=a3 

def get_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database")
        print(e)
        return None
    
# Function to update user logs in the database
import os

# Function to update user logs in the database
def update_user_logs(username, logs):
    conn = get_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            # Check if the user already exists in the table
            cursor.execute("SELECT * FROM logs WHERE username = %s", (username,))
            user_exists = cursor.fetchone()

            if user_exists:
                # Update the existing user's logs
                cursor.execute("UPDATE logs SET logs = %s WHERE username = %s", (logs, username))
            else:
                # Insert a new row for the user
                cursor.execute("INSERT INTO logs (username, logs) VALUES (%s, %s)", (username, logs))

            conn.commit()
            cursor.close()
        except psycopg2.Error as e:
            print("Error updating user logs:", e)
        finally:
            conn.close()

#########################################################################################
API_ENDPOINT = st.secrets['FASTAPI_ENDPOINT']
log_file_path = '/Users/sumanayanakonda/Desktop/Assignment-3/Streamlit/info.log'
if not os.path.exists(log_file_path):
    open(log_file_path, 'w').close()
logging.basicConfig(filename=log_file_path, level=logging.INFO)
#########################################################################################

#Function to get options list
def options_list():
    # Read the file names from a CSV file
    filename_df = pd.read_csv(st.secrets['FILENAME'], header=None)  # No header specified
    # Extract the options as a list
    options = filename_df[0].tolist()[1:] 
    options =  [i.strip() for i in options]
    options.append('All')
    return options


#Function to get token
def get_token(username, password):
    logging.info("Fetching token")
    payload = {
        'username': username,
        'password': password
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        logging.info("Sending request")
        response = requests.post(f"{API_ENDPOINT}/token", data=payload, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            st.success('Token retrieved successfully!')
            logging.info("Token retrieved successfully!")
            return token_data.get('access_token')
        else:
            st.error(f"Failed to retrieve token: {response.json().get('detail', 'No detail provided by server.')}")
            logging.info(f"Failed to retrieve token: {response.json().get('detail', 'No detail provided by server.')}")
    except requests.RequestException as e:
        st.error(f"An error occurred while retrieving token: {e}")
        logging.info(f"An error occurred while retrieving token: {e}")

    return None



#Function to get user details
def get_user_details(token, retries=1):
    """Function to get user details with a simple retry mechanism."""
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    for attempt in range(retries + 1):
        try:
            logging.info("Sending request")
            response = requests.get(f"{API_ENDPOINT}/users", headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as http_err:
            # Handle 401 Unauthorized separately
            if response.status_code == 401:
                if attempt < retries:
                    # Log the unauthorized attempt
                    logging.warning("Unauthorized. Retrying...")
                    continue
                else:
                    # Log the final unauthorized error
                    logging.info(f"401 Unauthorized: {response.json().get('detail', 'No detail provided by server.')}")
            else:
                # Log other HTTP errors
                logging.info(f"HTTP error occurred: {http_err}: {response.json().get('detail', 'No detail provided by server.')}")
        except Exception as e:
            # Log unexpected errors
            logging.info(f"An unexpected error occurred: {e}")
        # Wait a bit before retrying (if needed)
        if attempt < retries:
            time.sleep(1)
    return None

#Function to get answer
def handle_new_message(question, file, api_key, token):
    """Function to send a message to the chatbot and get a response."""
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
        logging.info("Sending request")
        response = requests.post(f"{API_ENDPOINT}/answer/", headers=headers, json=data)
        response.raise_for_status()
        logging.info("Response received")
        return response.json()
    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Response Body: {http_err.response.text}")
    except Exception as e:
        print(e,"culprit 2")
        st.error(f"An unexpected error occurred: {e}")


#Function to display chat history
def display_chat(history):
    logging.info("Displaying chat history")
    for idx, chat in enumerate(history):
        unique_id = str(uuid.uuid4()) 
        st.text_area(f"Q: {chat['question']}", value=chat['answer'], height=75, key=unique_id)


# Initialize session state for chat history
if 'chat_history' not in st.session_state:
    logging.info("Initializing chat history")
    st.session_state.chat_history = []

# Sidebar for user authentication
if 'access_token' not in st.session_state:
    logging.info("Displaying sign in form")
    with st.sidebar:
        st.subheader("Sign In")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Sign In"):
            print("fetching token", username, password)
            token = get_token(username, password)
            if token:
                st.session_state['access_token'] = token
                st.success('You are successfully signed in!')

#########################################################################################


st.title('Chatbot')

# Main page logic
if 'access_token' in st.session_state:
    logging.info("Displaying chat form")
    # Retrieve and display user details
    user_details = get_user_details(st.session_state.access_token, retries=1)
    if user_details:
        st.subheader(f"Welcome {user_details['username']}!")
        st.text(f"Email: {user_details['email']}")
        logging.info("User details displayed")
    
    # Input for new questions
    with st.form("chat_form"):
        options = options_list()
        question = st.text_input('Ask a question')
        file = st.selectbox("Select a file name:", options)
        openai_key = st.text_input('OpenAI Key', type="password")
        submit_button = st.form_submit_button(label='Submit')
        logging.info("Question submitted")
    
    if submit_button and question and file and openai_key:
        logging.info("Handling new message")
        print(st.session_state.access_token, "fectct")
        answer_data = handle_new_message(question, file, openai_key, st.session_state.access_token)
        print(answer_data)
        if answer_data:
            logging.info("Answer received")
            st.session_state.chat_history.append({
                'question': question,
                'answer': answer_data.get('choices', 'No answer returned')[0]['message']['content']
            })
            update_user_logs(user_details['username'], st.session_state.chat_history)
            display_chat(st.session_state.chat_history)
    else:
        update_user_logs(user_details['username'], st.session_state.chat_history)
        st.warning('Please enter ALL details to get an answer.')
        logging.info("No question submitted")
        display_chat(st.session_state.chat_history)
else:
    st.warning('Please sign in to use the chatbot.')
    logging.info("User not signed in")


