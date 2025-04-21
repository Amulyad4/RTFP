import os
import time
import json
import streamlit as st
import langdetect
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not GENAI_API_KEY:
    st.error("API key is missing! Please set GENAI_API_KEY in .env file.")
else:
    genai.configure(api_key=GENAI_API_KEY)

# Load responses dataset
responses = []
try:
    with open(r"C:\Users\Bhavani\OneDrive\Documents\Desktop\RTFP\responses.json", "r", encoding="utf-8") as file:
        responses = json.load(file)
except Exception as e:
    st.error(f"Error loading dataset: {e}")

# Streamlit Page Setup
st.set_page_config(page_title="Telugu Chatbot", layout="centered")
st.title("🤖 తెలుగు చాట్‌బాట్‌")

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Translation using Gemini ---
def translate_text(text):
    try:
        detected_lang = langdetect.detect(text)
        if detected_lang not in ["te", "en"]:
            detected_lang = "en" if all(ord(c) < 128 for c in text) else "te"
        if detected_lang == "te":
            source_lang = "Telugu"
            target_lang = "English"
        elif detected_lang == "en":
            source_lang = "English"
            target_lang = "Telugu"

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Translate the following text from {source_lang} to {target_lang}:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, 'text') else "⚠️ అనువాదం విఫలమైంది."
    except Exception as e:
        return f"❌ దోషం: {str(e)}"

# --- Summarization using Gemini ---
def summarize_text(text):
    try:
        detected_lang = langdetect.detect(text)
        lowered_text = text.lower()

        # If the text is in Telugu, summarize in Telugu; if in English, summarize in English
        if "summarize in english" in lowered_text:
            target_lang = "English"
        elif "summarize in telugu" in lowered_text or detected_lang == "te":
            target_lang = "Telugu"
        else:
            target_lang = "English"
        
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Summarize the following text in {target_lang}. Give only the summary:\n\n{text}"
        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, 'text') else "⚠️ సారాంశం విఫలమైంది."
    except Exception as e:
        return f"❌దోషం: {str(e)}"

# --- Dropdown Menu ---
task = st.selectbox("మీరు ఏ చర్యను చేయాలనుకుంటున్నారు?", ["Chat", "Translate", "Summarize"])

# --- Chat Mode ---
if task == "Chat":
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("మీరు ఎలా ఉన్నారు?"):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        cleaned_input = user_input.strip("?!.', ").lower()

        assistant_response = next(
            (item['output'] for item in responses
             if item['task'] == "chat" and item['input'].strip("?!.', ").lower() == cleaned_input),
            "క్షమించండి, నేను ఈ ప్రశ్నకు సమాధానం ఇవ్వలేను."
        )

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.04)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Translate Mode ---
elif task == "Translate":
    text = st.text_area("అనువదించడానికి టెక్స్ట్‌ను ఇవ్వండి:")
    if st.button("Translate"):
        if text.strip():
            result = translate_text(text.strip())
            st.success("### Translation Result")
            st.write(result)
        else:
            st.warning("Please enter some text.")

# --- Summarize Mode ---
elif task == "Summarize":
    text = st.text_area("సారాంశం కావలసిన టెక్స్ట్‌ను ఇవ్వండి:")
    
    # No need for a separate language option, auto-detects language for summarization
    if st.button("Summarize"):
        if text.strip():
            result = summarize_text(text.strip())
            st.success("### Summary")
            st.write(result)
        else:
            st.warning("Please enter some text.")
