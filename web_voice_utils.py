# web_voice_utils.py

import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import base64
from io import BytesIO

def autoplay_audio(audio_bytes: bytes):
    """
    A helper function to play audio bytes in Streamlit frontend.
    """
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio controls autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

def text_to_audio_bytes(text: str) -> bytes:
    """
    Converts text to audio bytes using gTTS.
    """
    try:
        tts = gTTS(text=text, lang='en', slow=False)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        return mp3_fp.read()
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {e}")
        return None

def audio_bytes_to_text(audio_bytes: bytes) -> str:
    """
    Converts audio bytes to text using SpeechRecognition.
    """
    if not audio_bytes:
        return ""
    
    r = sr.Recognizer()
    try:
        # The audio bytes from streamlit-mic-recorder are in WAV format
        # We need to wrap it in an AudioFile object
        with sr.AudioFile(BytesIO(audio_bytes)) as source:
            audio_data = r.record(source)
        
        # Recognize speech using Google Web Speech API
        text = r.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        st.warning("Google Speech Recognition could not understand the audio.")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return ""
    except Exception as e:
        st.error(f"An error occurred during speech recognition: {e}")
        return ""