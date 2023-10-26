import streamlit as st
import streamlit.pages.database as db
st.subheader("Create New Account")
new_user = st.text_input("Username")
new_password = st.text_input("Password", type='password')
new_email = st.text_input("Email")

if st.button("Signup"):
    if db.user_exists(new_user):
        st.warning("Username already exists. Choose a different one.")
    else:
                # Ideally, hash the password before saving
        db.add_user(new_user, new_email, new_password) 
        st.success("You have successfully created an account")
                
