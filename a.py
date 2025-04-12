import os
import random
import time
import streamlit as st
import google.generativeai as genai
import langdetect
from dotenv import load_dotenv

# Load API Key from .env file
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

if not GENAI_API_KEY:
    st.error("API key is missing! Please set GENAI_API_KEY in .env file.")
else:
    genai.configure(api_key=GENAI_API_KEY)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Translation Function ---
def translate_text(text):
    try:
        detected_lang = langdetect.detect(text)

        # Fallback logic for short/ambiguous inputs
        if detected_lang not in ["te", "en"]:
            detected_lang = "en" if all(ord(c) < 128 for c in text) else "te"

        if detected_lang == "te":
            source_lang = "Telugu"
            target_lang = "English"
        elif detected_lang == "en":
            source_lang = "English"
            target_lang = "Telugu"

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Translate the following text from {source_lang} to {target_lang}:\n{text}"
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "అనువాదం విఫలమైంది."
    
    except Exception as e:
        return f"దోషం: {str(e)}"

# --- Summarization Function ---
def summarize_text(text):
    try:
        detected_lang = langdetect.detect(text)
        lowered_text = text.lower()

        if "summarize in english" in lowered_text:
            target_lang = "English"
        elif "సారాంశం ఇవ్వండి" in lowered_text or detected_lang == "te":
            target_lang = "Telugu"
        else:
            target_lang = "English"

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Summarize the following text in {target_lang}:\n{text}"
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "సారాంశం విఫలమైంది."
    
    except Exception as e:
        return f"దోషం: {str(e)}"

# --- Predefined Chatbot Responses ---
responses = {
    "హలో": ["హాయ్! మీ రోజు ఎలా ఉంది?", "హలో! మీరు ఎలా ఉన్నారు?", "హలో! మీకు ఎలా సహాయం చేయగలను?"],
    "hi": ["హాయ్! మీరు ఎలా ఉన్నారు?"],
    "hlo": ["మీకు ఏమైనా సందేహాలు ఉన్నాయా?"],
    "మీరు ఎలా ఉన్నారు": ["నేను బాగా ఉన్నాను! మీరు ఎలా ఉన్నారు?"],
    "మీ పేరు ఏమిటి": ["నా పేరు తెలుగుబాట్!"],
    "మీరు నాకు సహాయం చేయగలరా": ["ఖచ్చితంగా! నేను మీకు ఏ విషయంపై సహాయం చేయగలను?"],
    "మీ రోజు ఎలా ఉంది": ["నా రోజు బాగుంది! మీది?"],
    "హాయ్! మీరు ఎలా ఉన్నారు?": ["నేను బాగా ఉన్నాను!"],
}
follow_up_questions = ["మీరు బాగా ఉన్నారా?", "మీ రోజు ఎలా ఉంది?"]

# --- UI Setup ---
st.set_page_config(page_title="Telugu Chatbot", layout="centered")
st.title("🤖 Telugu Chatbot")

task = st.selectbox("మీరు ఏ చర్యను చేయాలనుకుంటున్నారు?", ["Chat", "Translate", "Summarize"])

# --- Chat Mode ---
if task == "Chat":
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("మీరు ఎలా ఉన్నారు?"):
        cleaned_input = user_input.strip("?!.', ")
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        lowered_input = cleaned_input.lower()

        # Check for "can you translate"
        if lowered_input.startswith("can you translate") or lowered_input.startswith("భాష మార్చండి"):
            trigger_phrase = "can you translate" if "can you translate" in lowered_input else "భాష మార్చండి"
            to_translate = user_input[len(trigger_phrase):].strip()

            if not to_translate:
                assistant_response = "దయచేసి డ్రాప్‌డౌన్ మెనూను క్లిక్ చేసి, మీరు అనువదించాలనుకునే వాక్యాన్ని ఇవ్వండి."
            else:
                assistant_response = translate_text(to_translate)

        # Check for "can you summarize"
        elif lowered_input.startswith("can you summarize") or lowered_input.startswith("సారాంశం ఇవ్వగలవా"):
            trigger_phrase = "can you summarize" if "can you summarize" in lowered_input else "సారాంశం ఇవ్వగలవా"
            to_summarize = user_input[len(trigger_phrase):].strip()

            if not to_summarize:
                assistant_response = "దయచేసి డ్రాప్‌డౌన్ మెనూను క్లిక్ చేసి, మీరు సారాంశం కావాలనుకునే వచనాన్ని ఇవ్వండి."
            else:
                assistant_response = summarize_text(to_summarize)

        else:
            assistant_response = random.choice(responses.get(cleaned_input, ["క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను!"]))
            if cleaned_input == "hlo":
                assistant_response += "\n\n" + random.choice(follow_up_questions)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in assistant_response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Translation Mode ---
elif task == "Translate":
    text = st.text_area("అనువదించడానికి వచనాన్ని నమోదు చేయండి:")
    if st.button("Translate"):
        if text.strip():
            translation = translate_text(text)
            st.success("### Translation Result")
            st.write(translation)
        else:
            st.warning("దయచేసి వచనాన్ని నమోదు చేయండి.")

# --- Summarization Mode ---
elif task == "Summarize":
    text = st.text_area("సారాంశం ఇవ్వాలనుకుంటున్న వచనాన్ని నమోదు చేయండి:")
    if st.button("Summarize"):
        if text.strip():
            summary = summarize_text(text)
            st.success("### Summary Result")
            st.write(summary)
        else:
            st.warning("దయచేసి వచనాన్ని నమోదు చేయండి.")
