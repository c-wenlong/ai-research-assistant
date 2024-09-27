import streamlit as st
from openai import OpenAI


# Main function to initialize the app
def main():
    initialise_openai()
    display_chat_history()
    handle_user_input()


def initialise_openai():
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:  # Default model
        st.session_state["openai_model"] = st.secrets["OPENAI_MODEL"]

    if "messages" not in st.session_state:
        st.session_state.messages = []

    return client


# Function to display the chat history on the app
def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Function to handle user input and response generation
def handle_user_input():
    client = initialise_openai()  # Ensure OpenAI client is initialized

    # Accept user input
    if prompt := st.chat_input("Ask me anything :)"):
        # Add user input to the chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        display_user_message(prompt)

        # Generate assistant's response
        generate_assistant_response(client)


# Function to display user message
def display_user_message(prompt):
    with st.chat_message("user"):
        st.markdown(prompt)


# Function to generate and display assistant response using OpenAI
def generate_assistant_response(client):
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
        # st.markdown(response)  # Display the assistant's response

    # Add assistant response to the session state (chat history)
    st.session_state.messages.append({"role": "assistant", "content": response})


# Run the app
if __name__ == "__main__":
    st.title("Chat with Your Research Papers 📜")
    main()
