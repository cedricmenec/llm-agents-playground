import streamlit as st

st.set_page_config(page_title="Streamlit Application", layout="centered")

st.title("Welcome to the Streamlit Application")

user_input = st.text_input("Enter something:")
if user_input:
    st.write(f"You entered: {user_input}")
    