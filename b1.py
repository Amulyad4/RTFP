import os
import random
import time
import streamlit as st
import google.generativeai as genai
import langdetect
from dotenv import load_dotenv
from datasets import load_dataset

# Set page config FIRST - this must be the first Streamlit command
st.set_page_config(page_title="Telugu Chatbot with Dataset", layout="centered")

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

# --- Load Dataset ---
@st.cache_resource(show_spinner=False)
def load_telugu_dataset():
    try:
        with st.spinner("Loading Telugu dataset..."):
            dataset = load_dataset("Telugu-LLM-Labs/telugu_alpaca_yahma_cleaned_filtered_romanized")
            return dataset
    except Exception as e:
        st.error(f"Failed to load dataset: {str(e)}")
        return None

telugu_dataset = load_telugu_dataset()

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

# --- Predefined Responses ---
RESPONSES = {
    "greetings": {
        "te": ["హాయ్! మీ రోజు ఎలా ఉంది?", "హలో! మీరు ఎలా ఉన్నారు?", "హలో! మీకు ఎలా సహాయం చేయగలను?"],
        "en": ["Hi! How are you?", "Hello! How can I help you today?"]
    },
    "identity": {
        "te": ["నా పేరు తెలుగుబాట్!", "నేను తెలుగు చాట్ బాట్!"],
        "en": ["My name is TeluguBot!", "I'm a Telugu chatbot!"]
    }
}

# --- Find Relevant Response from Dataset ---
def get_dataset_response(user_input):
    if telugu_dataset is None:
        return None
    
    try:
        # Convert to lowercase for matching
        cleaned_input = user_input.lower().strip("?!.', ")
        
        # Search for similar instructions in the dataset
        possible_responses = []
        for example in telugu_dataset['train']:
            if example['input'] and cleaned_input in example['instruction'].lower():
                possible_responses.append(example['output'])
        
        return random.choice(possible_responses) if possible_responses else None
        
    except Exception as e:
        st.error(f"Error searching dataset: {str(e)}")
        return None

# --- Get Appropriate Response ---
def get_response(user_input):
    try:
        detected_lang = langdetect.detect(user_input) if len(user_input) > 3 else "te"
        
        # First try to get response from dataset
        dataset_response = get_dataset_response(user_input)
        if dataset_response:
            return dataset_response
        
        # Then check predefined responses
        if any(word in user_input.lower() for word in ["hello", "hi", "హలో", "హాయ్"]):
            return random.choice(RESPONSES["greetings"].get(detected_lang, ["హలో!"]))
        
        if any(word in user_input.lower() for word in ["who are you", "నువ్వెవరు", "మీ పేరు ఏమిటి"]):
            return random.choice(RESPONSES["identity"].get(detected_lang, ["నా పేరు తెలుగుబాట్!"]))
        
        # Finally use generative AI as fallback
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        prompt = f"Respond to this in {detected_lang} in a friendly, conversational way:\n{user_input}"
        response = model.generate_content(prompt)
        return response.text if response and hasattr(response, 'text') else "క్షమించండి, నేను అర్థం చేసుకోలేకపోయాను!"
    
    except Exception as e:
        st.error(f"Error in response generation: {str(e)}")
        return "దోషం: ప్రతిస్పందనను రూపొందించడంలో సమస్య ఏర్పడింది."

# --- Main App ---
st.title("🤖 తెలుగు చాట్‌బాట్ (Dataset Integrated)")

task = st.selectbox("మీరు ఏ చర్యను చేయాలనుకుంటున్నారు?", 
                   ["Chat", "Translate", "Summarize"])

# --- Chat Mode ---
if task == "Chat":
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("మీరు ఎలా ఉన్నారు?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display assistant response
        with st.chat_message("assistant"):
            response = get_response(prompt)
            
            # Stream the response
            message_placeholder = st.empty()
            full_response = ""
            
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

# --- Translation Mode ---
elif task == "Translate":
    st.header("🌍 అనువాదం")
    text = st.text_area("అనువదించడానికి వచనాన్ని నమోదు చేయండి:", height=150)
    if st.button("అనువదించు"):
        if text.strip():
            with st.spinner("అనువాదం చేస్తున్నాము..."):
                translation = translate_text(text)
                st.success("### అనువాద ఫలితం")
                st.write(translation)
        else:
            st.warning("దయచేసి వచనాన్ని నమోదు చేయండి.")

# --- Summarization Mode ---
elif task == "Summarize":
    st.header("📝 సారాంశం")
    text = st.text_area("సారాంశం ఇవ్వాలనుకుంటున్న వచనాన్ని నమోదు చేయండి:", height=150)
    if st.button("సారాంశం ఇవ్వండి"):
        if text.strip():
            with st.spinner("సారాంశం తయారు చేస్తున్నాము..."):
                summary = summarize_text(text)
                st.success("### సారాంశ ఫలితం")
                st.write(summary)
        else:
            st.warning("దయచేసి వచనాన్ని నమోదు చేయండి.")

# Sidebar info
with st.sidebar:
    st.header("About")
    st.write("This chatbot uses:")
    st.write("- Telugu-LLM-Labs dataset")
    st.write("- Google Gemini for generation")
    st.write("- Streamlit for interface")
    
    if telugu_dataset:
        st.success("Dataset loaded successfully!")
    else:
        st.error("Could not load dataset")