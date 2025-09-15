# voice_interface.py

import speech_recognition as sr
import pyttsx3

# Initialize Text-to-Speech engine
try:
    tts_engine = pyttsx3.init()
except Exception as e:
    print(f"Failed to initialize TTS engine: {e}")
    tts_engine = None

def speak(text):
    """Converts text to speech."""
    if not tts_engine:
        print("AI (TTS not available):", text)
        return
    
    print(f"AI: {text}")
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    """Listens for user's voice input and converts it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nListening... (Speak your answer clearly)")
        # Adjust for ambient noise to improve accuracy
        recognizer.adjust_for_ambient_noise(source, duration=1)
        # Set a pause threshold to detect the end of speech
        recognizer.pause_threshold = 1.5 
        audio = recognizer.listen(source)

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        speak("Sorry, I did not understand that. Could you please repeat?")
        return listen() # Ask the user to repeat
    except sr.RequestError:
        speak("Sorry, my speech service is currently unavailable. We'll have to skip this question.")
        return ""