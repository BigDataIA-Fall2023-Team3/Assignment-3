# app.py
import streamlit as st

# Make sure you import the app functions directly if they are at the module level.
from others.home import app as home_app
from others.sign_up import app as signup_app
from others.sign_in import app as signin_app

PAGES = {
    "Home": home_app,
    "Sign Up": signup_app,
    "Sign In": signin_app,
}

def main():
    """Main function of the App"""
    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", list(PAGES.keys()))

    # Directly call the function mapped to the choice.
    PAGES[choice]()

if __name__ == "__main__":
    main()
        
