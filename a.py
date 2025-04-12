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
    "hello": ["హాయ్! మీ రోజు ఎలా ఉంది?", "హలో! మీరు ఎలా ఉన్నారు?", "హలో! మీకు ఎలా సహాయం చేయగలను?"],
    
    "హాయ్": ["హాయ్! మీరు ఎలా ఉన్నారు?"],
    "hi": ["హాయ్! మీరు ఎలా ఉన్నారు?"],
    
    "మీరు ఎలా ఉన్నారు": ["నేను బాగా ఉన్నాను! మీరు ఎలా ఉన్నారు?"],
    "meeru ela unnaru": ["నేను బాగా ఉన్నాను! మీరు ఎలా ఉన్నారు?"],
    
    "ఎలா ఉన్నావ్": ["నేను బాగా ఉన్నాను! మీరు ఎలా ఉన్నారు?"],
    "ela unnav": ["నేను బాగా ఉన్నాను! మీరు ఎలా ఉన్నారు?"],
    
    "మీ పేరు ఏమిటి": ["నా పేరు తెలుగుబాట్!"],
    "mee peru emiti": ["నా పేరు తెలుగుబాట్!"],
    
    "మీ రోజు ఎలా ఉంది": ["నా రోజు బాగుంది! మీది?"],
    "mee roju ela undi": ["నా రోజు బాగుంది! మీది?"],
    
    "బాగున్నావా": ["అవును!మీరు ఎలా ఉన్నారు? "],
    "bagunnava": ["అవును! మీరు ఎలా ఉన్నారు?"],

    "ఎమి చేస్తున్నావు": ["ఇప్పుడే మీతో మాట్లాడుతున్నాను!", "మీ ప్రశ్నకు సమాధానం ఇవ్వడానికి సిద్ధంగా ఉన్నాను!"],
    "em chestunnav": ["మీతో చాట్ చేస్తున్నాను!", "ఇదే, మీ సందేహాలను పరిష్కరించడానికి సిద్ధంగా ఉన్నాను!"],

    "నువ్వెవరు": ["నేను తెలుగుబాట్! మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను."],
    "nuvveru": ["నేను తెలుగుబాట్! మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను."],

    "ధన్యవాదాలు": ["స్వాగతం!", "ఎప్పుడైనా సహాయం చేయడానికి సిద్ధంగా ఉన్నాను!"],
    "thanks": ["స్వాగతం!", "ఎప్పుడైనా సహాయం చేయడానికి సిద్ధంగా ఉన్నాను!"],

    "సాయపడతావా": ["ఖచ్చితంగా! ఏం కావాలో చెప్పండి."],
    "saayapadutava": ["ఖచ్చితంగా! ఏం కావాలో చెప్పండి."],

    "ఎంత గంటయ్యింది": ["క్షమించండి, నాకు సమయం తెలియదు. కానీ మీరు ఫోన్ చూడండి 😅"],
    "time enta": ["క్షమించండి, నాకు సమయం తెలియదు. కానీ మీరు ఫోన్ చూడండి 😅"],

    "నీకు తెలుగు వచ్చా": ["అవును! నాకు తెలుగు చాలా బాగొచ్చును!"],
    "neeku telugu vaccha": ["అవును! నాకు తెలుగు చాలా బాగొచ్చును!"],

    "నీకు ఇంగ్లీష్ వచ్చా": ["అవును, నాకు ఇంగ్లీష్ కూడా వచ్చును."],
    "neeku english vaccha": ["అవును, నాకు ఇంగ్లీష్ కూడా వచ్చును."],

    "శుభోదయం": ["శుభోదయం! మీ రోజు ఆనందంగా సాగాలని కోరుకుంటున్నాను."],
    "good morning": ["శుభోదయం! మీ రోజు ఆనందంగా సాగాలని కోరుకుంటున్నాను."],

    "శుభసంధ్యా": ["శుభసంధ్యా! ఈ రోజు ఎలా ఉంది?"],
    "good evening": ["శుభసంధ్యా! ఈ రోజు ఎలా ఉంది?"],


    "మీ రోజు ఎలా ఉంది": ["నా రోజు బాగుంది! మీది?"],
    "mee roju ela undi": ["నా రోజు బాగుంది! మీది?"],

    "ఎం చేస్తున్నావ్": ["మీతో మాట్లాడుతున్నాను!", "ఇప్పుడే రిలాక్స్ అవుతున్నాను."],
    "em chestunnav": ["మీతో మాట్లాడుతున్నాను!", "ఇప్పుడే రిలాక్స్ అవుతున్నాను."],

    "బ్రేక్‌ఫాస్ట్ చేశావా": ["ఓ అవును! మీరు చేశారా?"],
    "breakfast chesava": ["ఓ అవును! మీరు చేశారా?"],

    "మీలో బిజీనా": ["కొంచెం. కానీ మీకోసం టైమ్ ఉంది!"],
    "are you busy": ["కొంచెం. కానీ మీకోసం టైమ్ ఉంది!"],

    "మీ పేరు ఏమిటి": ["నా పేరు తెలుగుబాట్!"],
    "mee peru emiti": ["నా పేరు తెలుగుబాట్!"],

    "నువ్వెవరు": ["నేను తెలుగుబాట్! మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను."],
    "nuvveru": ["నేను తెలుగుబాట్! మీకు సహాయం చేయడానికి ఇక్కడ ఉన్నాను."],

    # Jokes
    "ఒక జోక్ చెప్తావా": ["ఎందుకు కంప్యూటర్ చింతించదు? ఎందుకంటే అది వైరస్‌లను తొలగించగలదు! 😂"],
    "cheppu oka joke": ["పెన driveకి ఎందుకు కలవరంగా ఉంది? ఎందుకంటే అది 'full' అయిపోయింది! 😄"],

    "హాస్యం చెప్తావా": ["పుస్తకం జైలుకు ఎందుకు వెళ్ళింది? ఎందుకంటే అది 'cover' లో దాచబడింది! 😂"],
    "hasyam cheppu": ["సార్ అంటే ఎవరంటే... క్లాస్‌లోకి వచ్చి ప్రశ్నలే అడిగే వాడు! 😆"],

    # Emotional support
    "నా మనస్సు బాదగా ఉంది": ["బాధగా ఉన్నప్పుడు మాట్లాడటం మంచిదే. నేను ఇక్కడ ఉన్నాను."],
    "naku badhaga undi": ["ఇది తాత్కాలికమే. మీరు బలంగా ఉన్నారు."],

    "నాకు ఒంటరిగా ఉంది": ["మీరు ఒంటరిగా లేరండి. నేను ఇక్కడ ఉన్నాను మీతో మాట్లాడడానికి."],
    "naku ontariga undi": ["మీరు ఒంటరిగా లేరండి. నేను ఇక్కడ ఉన్నాను మీతో మాట్లాడడానికి."],

    "నాకు ఏం చేయాలో అర్థం కావడం లేదు": ["ఆలస్యం చేయకండి, ఒక్కసారి బ్రేక్ తీసుకోండి. తర్వాత తేలికగా అనిపిస్తుంది."],
    "naku em cheyyalo ardham kavatam ledu": ["తగినంత విశ్రాంతి తీసుకోండి. నెమ్మదిగా ముందుకెళ్ళండి."],

    "నాకు భయం గా ఉంది": ["నిజమైన ధైర్యం అంటే భయాన్ని అంగీకరించడం. మీరు ధైర్యంగా ఉన్నారు!"],
    "naku bhayam ga undi": ["చింతించకండి. మీకు సహాయం అందుతుంది. మీరు బలంగా ఉన్నారు."],

    # Gratitude
    "ధన్యవాదాలు": ["స్వాగతం! మీకు ఎప్పుడైనా సహాయం చేసేందుకు సిద్ధంగా ఉన్నాను."],
    "thanks": ["స్వాగతం! ఎప్పుడైనా సాయం కావాలంటే చెప్పండి."],

    # Support
    "నాకు సహాయం కావాలి": ["తప్పకుండా! ఏ విషయమై సహాయం కావాలి?"],
    "naku sahayam kavali": ["చెప్పండి, నేను మీకు సహాయం చేస్తాను."],

    "మీరు నాకు సహాయం చేస్తారా": ["అవును, నేనిక్కడే ఉన్నాను సహాయం చేయడానికి."],
    "meeru naaku sahayam chestara": ["అవును, ఏ విషయమై సహాయం కావాలో చెప్పండి."],

}

follow_up_questions = ["మీరు బాగా ఉన్నారా?", "మీ రోజు ఎలా ఉంది?"]

# --- UI Setup ---
st.set_page_config(page_title="Telugu Chatbot Translator & Summarizer", layout="centered")
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
                assistant_response = "Sure! Just click the drop-down menu and provide the text you'd like to translate."
            else:
                assistant_response = translate_text(to_translate)

        # Check for "can you summarize"
        elif lowered_input.startswith("can you summarize") or lowered_input.startswith("సారాంశం ఇవ్వగలవా"):
            trigger_phrase = "can you summarize" if "can you summarize" in lowered_input else "సారాంశం ఇవ్వగలవా"
            to_summarize = user_input[len(trigger_phrase):].strip()

            if not to_summarize:
                assistant_response = "Sure! Just click the drop-down menu and provide the text you'd like summarized."
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
