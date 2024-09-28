import streamlit as st

st.set_page_config(
    page_title="AIRA",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("AIRA")
st.sidebar.markdown("<h5>Your Intelligent Research Assistant</h5>", unsafe_allow_html=True)  # Custom HTML for smaller title

st.title("Welcome to the Streamlit App")