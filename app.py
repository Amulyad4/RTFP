import os
import streamlit as st
import google.generativeai as genai
import langdetect  # To detect the language of input text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GENAI_API_KEY = os.getenv("GENAI_API_KEY")

# Configure API
if not GENAI_API_KEY:
    st.error("API key is missing! Please set GENAI_API_KEY in .env file.")
else:
    genai.configure(api_key=GENAI_API_KEY)

# Translation function with improved handling of short phrases
def translate_text(text):
    try:
        # Manually check for some common short phrases that might cause detection issues
        short_phrases = ["hi", "hello", "how are you", "good morning", "good evening", "bye"]
        
        # Normalize the text to lowercase and check if it's a common short phrase
        normalized_text = text.strip().lower()

        if normalized_text in short_phrases:
            # If it's a short phrase, directly map it to a translation
            if normalized_text == "hi":
                return "హాయ్"
            elif normalized_text == "hello":
                return "హలో"
            elif normalized_text == "how are you":
                return "మీరు ఎలా ఉన్నారు?"
            elif normalized_text == "good morning":
                return "శుభోదయం"
            elif normalized_text == "good evening":
                return "శుభ సాయంత్రం"
            elif normalized_text == "bye":
                return "వీడ్కోలు"
        
        # If it's not a short phrase, proceed with language detection
        detected_lang = langdetect.detect(text)

        if detected_lang == "te":
            source_lang = "Telugu"
            target_lang = "English"
        elif detected_lang == "en":
            source_lang = "English"
            target_lang = "Telugu"
        else:
            return "⚠️ Sorry, only Telugu and English are supported."

        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = (
            f"You are a professional translator. Translate the following short or long text "
            f"from {source_lang} to {target_lang}. Be accurate even with casual or small phrases.\n\n"
            f"Text: \"{text}\""
        )

        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, 'text') else "⚠️ Translation failed."

    except Exception as e:
        return f"❌ Error: {str(e)}"

# Streamlit UI
st.set_page_config(page_title="Telugu Chatbot Translator", layout="centered")
st.title("🌍 Telugu Chatbot Translator")

# User input
text = st.text_area("Enter text to translate:", "")

if st.button("Translate"):
    if text.strip():
        translation = translate_text(text)
        st.success("### Translation Result")
        st.write(translation)
    else:
        st.warning("Please enter some text to translate.")
