import streamlit as st
import requests

# Define the backend endpoint (replace with your actual endpoint URL)
BACKEND_URL = "https://your-backend-endpoint.com/search"

# Streamlit configuration for minimalistic appearance
st.set_page_config(page_title="Search App", layout="centered")

# CSS to make it look slick and minimalistic
st.markdown(
    """
    <style>
    .main {
        padding-top: 50px;
    }
    .stTextInput > div > input {
        font-size: 16px;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ddd;
        width: 100%;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
        font-size: 16px;
        cursor: pointer;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Minimalistic search bar UI
st.title("Search")
search_query = st.text_input("Enter your search query", "")

# Search button to trigger the API request
if st.button("Search"):
    if search_query:
        # Make a request to the backend API
        response = requests.get(BACKEND_URL, params={"query": search_query})

        if response.status_code == 200:
            results = response.json()
            st.success("Results found:")
            for result in results.get("data", []):
                st.write(result)
        else:
            st.error("Error retrieving search results")
    else:
        st.warning("Please enter a search query")
