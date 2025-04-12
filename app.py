import os
import streamlit as st
import google.generativeai as genai
import langdetect  # To detect the language of input text
from dotenv import load_dotenv

load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    st.error("API key is missing! Please set GENAI_API_KEY in .env file.")
else:
    genai.configure(api_key=GENAI_API_KEY)

# Function to detect language and translate accordingly
# Update this section to handle cases where the detected language isn't Telugu or English
def translate_text(text):
    try:
        detected_lang = langdetect.detect(text)  # Detect input language
        if detected_lang == "te":
            source_lang = "Telugu"
            target_lang = "English"
        elif detected_lang == "en":
            source_lang = "English"
            target_lang = "Telugu"
        else:
            return "Sorry, I currently only support Telugu and English. Please enter text in either language."

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Translate the following text from {source_lang} to {target_lang}:\n{text}"
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "Translation failed."
    
    except Exception as e:
        return f"Sorry, an error occurred during translation: {str(e)}"


# Streamlit UI
st.set_page_config(page_title="Telugu Chatbot Translator", layout="centered")
st.title("🌍 Telugu Chatbot Translator")

# User Input
text = st.text_area("Enter text to translate:", "")

if st.button("Translate"):
    if text.strip():
        translation = translate_text(text)
        st.success("### Translation Result")
        st.write(translation)
    else:
        st.warning("Please enter some text to translate.")

