import streamlit as st  # Import Streamlit
import random  # Import random for generating responses
import time  # Import time for typing effect

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="సాధారణ చాట్", page_icon="💬", layout="wide")

# --- Custom CSS for Visual Enhancements ---
st.markdown("""
    <style>
        .stChatMessage { border-radius: 12px; padding: 10px; margin-bottom: 10px; }
        .stChatMessageUser { background-color: #DCF8C6; color: black; }
        .stChatMessageAssistant { background-color: #EAEAEA; color: black; }
        .stTitle { text-align: center; font-size: 32px; color: #007bff; }
    </style>
""", unsafe_allow_html=True)

# --- Title of the Chatbot ---
st.markdown("<h1 class='stTitle'>🤖 సాధారణ చాట్</h1>", unsafe_allow_html=True)
st.write("🌟 **తెలుగులో మీ స్నేహితుడిని మాట్లాడించుకోండి!**")

# --- Initialize Chat History in Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat Messages ---
for message in st.session_state.messages:
    role_class = "stChatMessageUser" if message["role"] == "user" else "stChatMessageAssistant"
    with st.chat_message(message["role"]):
        st.markdown(f"<div class='{role_class}'>{message['content']}</div>", unsafe_allow_html=True)

# --- User Input Handling ---
if prompt := st.chat_input("మీరు ఎలా ఉన్నారు?"):
    # --- Display User Message ---
    with st.chat_message("user"):
        st.markdown(f"<div class='stChatMessageUser'>{prompt}</div>", unsafe_allow_html=True)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # --- Generate Assistant Response ---
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # --- Response Variations ---
        responses = [
            "హలో! నేను మీకు ఎలా సహాయం చేయగలనా? 😊",
            "హాయ్, మీరు ఎలా ఉన్నారు? 😃",
            "మీ ప్రశ్నకు సమాధానం ఇక్కడే! 🤔",
            "మీరు నా గురించి ఏమైనా అడగాలనుకుంటున్నారా? 🧐"
        ]
        assistant_response = random.choice(responses)

        # --- Typing Effect ---
        for word in assistant_response.split():
            full_response += word + " "
            time.sleep(0.05)
            message_placeholder.markdown(full_response + "▌")

        message_placeholder.markdown(full_response)

    # --- Store Bot Response in Chat History ---
    st.session_state.messages.append({"role": "assistant", "content": full_response})
