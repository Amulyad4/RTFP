import streamlit as st  # Import the Streamlit library
import random  # Import the random library
import time  # Import the time library

# Creating a title for our streamlit web application
st.title("సాధారణ చాట్")  # Set the title of the web application (in Telugu)

# Initializing the chat history in the session state
if "messages" not in st.session_state:  # Check if "messages" exists in session state
    st.session_state.messages = []  # Initialize "messages" as an empty list

# Displaying the existing chat messages from the user and the chatbot
for message in st.session_state.messages:  # For every message in the chat history
    with st.chat_message(message["role"]):  # Create a chat message box
        st.markdown(message["content"])  # Display the content of the message

# Accepting the user input and adding it to the message history
if prompt := st.chat_input("మీరు ఎలా ఉన్నారు?"):  # If user enters a message
    with st.chat_message("user"):  # Display user's message in a chat message box
        st.markdown(prompt)  # Display the user's message
    st.session_state.messages.append({"role": "user", "content": prompt})  # Add user's message to chat history

# Generating and displaying the assistant's response in Telugu
with st.chat_message("assistant"):  # Create a chat message box for the assistant's response
    message_placeholder = st.empty()  # Create an empty placeholder for the assistant's message
    full_response = ""  # Initialize an empty string for the full response
    assistant_response = random.choice([
        "హలో! నేను మీకు ఎలా సహాయం చేయగలనా?",
        "హాయ్, మనిషి! నేను మీకు ఎలా సహాయం చేయగలను?",
        "మీకు సహాయం కావాలా?"
    ])  # Select assistant's response randomly in Telugu

    # Simulate "typing" effect by gradually revealing the response
    for chunk in assistant_response.split():  # For each word in the response
        full_response += chunk + " "
        time.sleep(0.05)  # Small delay between each word
        message_placeholder.markdown(full_response + "▌")  # Update placeholder with current full response and a blinking cursor

    message_placeholder.markdown(full_response)  # Remove cursor and display full response
    st.session_state.messages.append({"role": "assistant", "content": full_response})  # Add assistant's response to chat history
