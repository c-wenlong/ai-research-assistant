import streamlit as st
import requests
import json
import time

# Define the backend endpoint (replace with your actual endpoint URL)
BACKEND_URL = "http://127.0.0.1:5000/web_search"

# Streamlit configuration for minimalistic appearance
st.set_page_config(page_title="Search App", layout="centered")

# Minimalistic search bar UI
st.title("Search")
search_query = st.text_input("Enter your search query", "")

# Search button to trigger the API request
if st.button("Search"):
    if search_query:
        with st.spinner("Loading... Please wait."):
            try:
                # Sending request to the backend API
                print(f"Sending query: {search_query}")
                response = requests.post(BACKEND_URL, json={"query": search_query}, stream=True)
                
                # Check for the response status
                if response.status_code == 200:
                    st.success("Search completed successfully.")
                    
                    # Reading the streamed response
                    for chunk in response.iter_lines():
                        if chunk:
                            # Decode the chunk and process it as per backend response structure
                            result = json.loads(chunk.decode('utf-8'))
                            st.write(result)
                            time.sleep(1)  # Simulate delay between chunks

                else:
                    st.error(f"Error: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Error while contacting backend: {str(e)}")

    else:
        st.warning("Please enter a search query")