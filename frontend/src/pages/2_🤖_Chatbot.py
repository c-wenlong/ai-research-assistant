import os
import streamlit as st
import requests  # Import the requests library


# Main function to initialize the app
def main():
    initialise_openai()
    display_chat_history()
    handle_user_input()


def initialise_openai():
    # You might still want to keep this for OpenAI integration
    if "openai_model" not in st.session_state:  # Default model
        st.session_state["openai_model"] = os.getenv("OPENAI_API_KEY")

    if "messages" not in st.session_state:
        st.session_state.messages = []


# Function to display the chat history on the app
def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Function to handle user input and response generation
def handle_user_input():
    # Accept user input
    if prompt := st.chat_input("Ask me anything :)"):
        # Add user input to the chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_user_message(prompt)

        # Generate assistant's response
        generate_assistant_response(prompt)


# Function to display user message
def display_user_message(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)


# Function to generate and display assistant response using Flask
def generate_assistant_response(user_input):
    with st.chat_message("assistant"):
        # Call the Flask API
        response = requests.post(
            "https://aira-77ad510980a9.herokuapp.com/api/get_response", json={"user_input": user_input}
        )

        if response.status_code == 200:
            response_data = response.json()
            assistant_response = response_data.get("response")

            # Add assistant response to the session state (chat history)
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_response}
            )
            st.markdown(assistant_response)  # Display the assistant's response
        else:
            st.markdown("Error: Unable to get response from the server.")


# Run the app
if __name__ == "__main__":
    st.title("Chat with Your Research Papers 📜")
    main()
