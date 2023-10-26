import streamlit as st
import streamlit.pages.database as db

st.title("Welcome to SEC Data Vector Search Platform!")

st.sidebar.subheader("Enter Login Details")

username = st.sidebar.text_input("User Name")
password = st.sidebar.text_input("Password", type='password')
if st.sidebar.button("Login"):
    if db.check_user(username, password):
        st.success("Logged in Successfully")
        st.write("Welcome, ", username)
    else:
        st.warning("Incorrect Username/Password")