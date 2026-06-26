import os
import time
import json
import streamlit as st
import langdetect
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("API key is missing! Please set GOOGLE_API_KEY in .env file.")
else:
    genai.configure(api_key=GOOGLE_API_KEY)

# Load responses dataset
responses = []
try:
    with open("responses.json", "r", encoding="utf-8") as file:
        responses = json.load(file)
except Exception as e:
    st.error(f"Error loading dataset: {e}")

# Streamlit Page Setup
st.set_page_config(
    page_title="తెలుగు చాట్‌బాట్ - Telugu Chatbot",
    page_icon="🤖",
    layout="centered"
)

# Custom Premium Styling
st.markdown("""
<style>
/* Import Outfit and Inter fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', 'Inter', sans-serif;
}

/* Main title styling */
.main-title {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    background: linear-gradient(135deg, #1E88E5, #D81B60);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    text-align: center;
    margin-bottom: 0.1rem;
}

.subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 1.1rem;
    color: #888888;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Card-like borders for results */
.result-card {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 20px;
    margin-top: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

/* Adjust tab labels styling */
button[data-baseweb="tab"] {
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
}
</style>
""", unsafe_allow_html=True)

# Page header
st.markdown('<h1 class="main-title">🤖 తెలుగు చాట్‌బాట్</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Multi-functional AI Assistant for Telugu & English</p>', unsafe_allow_html=True)

# Session state initialization for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Language Detection Helper ---
def detect_language(text):
    try:
        # Check if there are Telugu characters
        has_telugu = any('\u0c00' <= char <= '\u0c7f' for char in text)
        if has_telugu:
            return "te"
        
        # Fallback to standard detect
        return langdetect.detect(text)
    except Exception:
        # Default check based on simple ascii presence
        if any(ord(c) < 128 for c in text if c.isalnum()):
            return "en"
        return "te"

# --- Translation Logic ---
def translate_text(text):
    try:
        # Check for common short phrases
        short_phrases = {
            "hi": "హాయ్",
            "hello": "హలో",
            "how are you": "మీరు ఎలా ఉన్నారు?",
            "good morning": "శుభోదయం",
            "good evening": "శుభ సాయంత్రం",
            "bye": "వీడ్కోలు"
        }
        
        normalized_text = text.strip().lower().strip("?!.,")
        if normalized_text in short_phrases:
            return short_phrases[normalized_text]
        
        detected_lang = detect_language(text)
        if detected_lang == "te":
            source_lang = "Telugu"
            target_lang = "English"
        else:
            source_lang = "English"
            target_lang = "Telugu"

        model = genai.GenerativeModel("gemini-3.5-flash")
        prompt = (
            f"You are a professional translator. Translate the following text from {source_lang} to {target_lang}. "
            f"Give ONLY the translation. Do not include any explanations, side notes, or markdown formatting.\n\n"
            f"Text: \"{text}\""
        )
        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, 'text') else "⚠️ అనువాదం విఫలమైంది."
    except Exception as e:
        return f"❌ దోషం: {str(e)}"

# --- Summarization Logic ---
def summarize_text(text):
    try:
        detected_lang = detect_language(text)
        lowered_text = text.lower()

        # Decide summary target language
        if "summarize in english" in lowered_text:
            target_lang = "English"
        elif "summarize in telugu" in lowered_text:
            target_lang = "Telugu"
        elif detected_lang == "te":
            target_lang = "Telugu"
        else:
            target_lang = "English"
        
        model = genai.GenerativeModel("gemini-3.5-flash")
        prompt = (
            f"Summarize the following text in {target_lang}. "
            f"Provide only the summary, with no introduction, metadata, or greetings:\n\n{text}"
        )
        response = model.generate_content(prompt)
        return response.text.strip() if response and hasattr(response, 'text') else "⚠️ సారాంశం విఫలమైంది."
    except Exception as e:
        return f"❌ దోషం: {str(e)}"

# --- Navigation Setup (Tab-based) ---
tab_chat, tab_translate, tab_summarize = st.tabs([
    "💬 చాట్ (Chat)",
    "🌍 అనువాదం (Translate)",
    "📝 సారాంశం (Summarize)"
])

# ==================== CHAT TAB ====================
with tab_chat:
    # Sidebar control within chat or directly at page level (let's add a clear button)
    col1, col2 = st.columns([6, 2])
    with col1:
        st.subheader("తెలుగుబాట్ తో మాట్లాడండి")
    with col2:
        if st.button("Reset Chat", key="reset_chat_btn"):
            st.session_state.messages = []
            st.rerun()

    # Display welcome message if no history
    if not st.session_state.messages:
        with st.chat_message("assistant"):
            st.markdown("హలో! నేను తెలుగుబాట్. మీకు ఏ విధంగా సహాయపడగలను? (Hello! I am TeluguBot. How can I help you today?)")

    # Render message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if user_input := st.chat_input("ఇక్కడ సందేశాన్ని నమోదు చేయండి... (Type a message here...)"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Match logic
        cleaned_input = user_input.strip("?!.', ").lower()
        
        # 1. Search in predefined responses
        assistant_response = next(
            (item['output'] for item in responses
             if item['task'] == "chat" and item['input'].strip("?!.', ").lower() == cleaned_input),
            None
        )

        # 2. AI Fallback (Gemini-1.5-flash with history context)
        if not assistant_response:
            try:
                system_prompt = (
                    "You are a helpful, polite, and friendly Telugu AI assistant named 'TeluguBot' (తెలుగుబాట్). "
                    "Respond to the user naturally. If they write to you in Telugu, respond in fluent Telugu. "
                    "If they write to you in English, respond in English or Telugu as appropriate. "
                    "Keep your responses relatively concise, helpful, and natural."
                )
                model = genai.GenerativeModel("gemini-3.5-flash", system_instruction=system_prompt)
                
                # Construct history for Gemini API
                gemini_history = []
                for msg in st.session_state.messages[:-1]:  # exclude latest user msg
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})
                
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(user_input)
                assistant_response = response.text.strip() if response and hasattr(response, 'text') else "క్షమించండి, నేను దీనికి సమాధానం ఇవ్వలేకపోయాను."
            except Exception as e:
                assistant_response = f"❌ AI కనెక్షన్ విఫలమైంది: {str(e)}"

        # Output with typewriter effect
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            # Handle list of words for typing effect
            words = assistant_response.split(" ")
            for chunk in words:
                full_response += chunk + " "
                time.sleep(0.04)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response.strip())

        st.session_state.messages.append({"role": "assistant", "content": full_response.strip()})

# ==================== TRANSLATE TAB ====================
with tab_translate:
    st.subheader("భాషా అనువాదం (Language Translation)")
    st.markdown("తెలుగు మరియు ఇంగ్లీష్ మధ్య అనువదించండి (Translate between Telugu and English).")
    
    text_to_translate = st.text_area("టెక్స్ట్‌ను నమోదు చేయండి (Enter text):", key="trans_input", height=150)
    
    if st.button("అనువదించు (Translate)", key="trans_btn"):
        if text_to_translate.strip():
            with st.spinner("అనువదిస్తోంది... (Translating...)"):
                result = translate_text(text_to_translate.strip())
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.success("### అనువాద ఫలితం (Translation Result)")
                st.write(result)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("అనువదించడానికి దయచేసి టెక్స్ట్‌ను నమోదు చేయండి. (Please enter some text to translate.)")

# ==================== SUMMARIZE TAB ====================
with tab_summarize:
    st.subheader("సారాంశం (Text Summarization)")
    st.markdown("పెద్ద వచనాన్ని చిన్న సారాంశంగా మార్చండి (Summarize long text into a shorter summary).")
    
    text_to_summarize = st.text_area("సారాంశం కోసం టెక్స్ట్‌ను నమోదు చేయండి (Enter text to summarize):", key="summ_input", height=150)
    
    if st.button("సారాంశం చేయి (Summarize)", key="summ_btn"):
        if text_to_summarize.strip():
            with st.spinner("సారాంశం చేస్తోంది... (Summarizing...)"):
                result = summarize_text(text_to_summarize.strip())
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.success("### సారాంశం ఫలితం (Summary Result)")
                st.write(result)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("సారాంశం కోసం దయచేసి టెక్స్ట్‌ను నమోదు చేయండి. (Please enter some text to summarize.)")
