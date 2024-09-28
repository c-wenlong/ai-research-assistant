# import streamlit as st
# import requests
# import time  # Import time for simulating a loading delay (optional)
# import json

# # Define the backend endpoint (replace with your actual endpoint URL)
# BACKEND_URL = "http://127.0.0.1:5000/web_search"

# # Streamlit configuration for minimalistic appearance
# st.set_page_config(page_title="Search App", layout="centered")

# # CSS to make it look slick and minimalistic
# st.markdown(
#     """
#     <style>
#     .main {
#         padding-top: 50px;
#     }
#     .stTextInput > div > input {
#         font-size: 16px;
#         padding: 10px;
#         border-radius: 5px;
#         border: 1px solid #ddd;
#         width: 100%;
#     }
#     .stButton > button {
#         background-color: #4CAF50;
#         color: white;
#         padding: 10px 20px;
#         border-radius: 5px;
#         border: none;
#         font-size: 16px;
#         cursor: pointer;
#     }
#     .stButton > button:hover {
#         background-color: #45a049;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# # Minimalistic search bar UI
# st.title("Search")
# search_query = st.text_input("Enter your search query", "")

# # Search button to trigger the API request
# if st.button("Search"):
#     if search_query:
#         with st.spinner("Loading... Please wait."):  # Show loading spinner
#             print(search_query)
#             # Make a request to the backend API using JSON
#             print("Button clicked, sending request...")
#             response = requests.post(BACKEND_URL, json={"query": search_query})
#             print("Request sent to backend")
#             print("Response status code:", response.status_code)
#             print("Response text:", response.text)  # Print raw response

#             # Optional: Simulate loading time (for testing)
#             time.sleep(2)  # Remove this line in production

#             if response.status_code == 200:
#                 print("Success! Message received:", response.json())
#                 try:
#                     results = response.json()
#                     print("API Response:", results)  # Log the raw response for debugging
#                     if results.get("message"):
#                         st.session_state.results = results["message"]
#                         st.success("Results found!")
#                     else:
#                         st.error("No data returned from the API.")
#                         print("Response structure:", results)
#                 except json.JSONDecodeError:
#                     st.error("Failed to decode JSON response.")
#                     print("Response content:", response.content)
#             else:
#                 st.error(f"Error retrieving search results: {response.status_code} - {response.text}")

#     else:
#         st.warning("Please enter a search query")

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