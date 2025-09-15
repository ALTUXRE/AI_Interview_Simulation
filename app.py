# app.py (v3.1 - Complete Code with Professional Dark Theme)

import streamlit as st
from streamlit_mic_recorder import mic_recorder

# Import our backend and utility modules
import interviewer_ai as ai
import database as db
import web_voice_utils as voice

# --- Page Configuration ---
st.set_page_config(
    page_title="ProVoice AI Interviewer",
    page_icon="💼",
    layout="wide"
)

# --- Custom CSS for a polished, modern look ---
def load_css():
    st.markdown("""
        <style>
            /* Import Google Font */
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

            /* Main app styling */
            html, body, [class*="st-"] {
                font-family: 'Poppins', sans-serif;
                color: #e0e0e0; /* Light text for readability */
            }
            .stApp {
                background-color: #1e1e1e; /* Dark background */
            }

            /* Sidebar styling */
            [data-testid="stSidebar"] {
                background-color: #252526;
                border-right: 1px solid #333333;
            }

            /* Main content headers */
            h3 {
                 color: #ffffff;
                 font-size: 1.5rem;
                 padding-bottom: 1rem;
                 border-bottom: 2px solid #333333;
            }

            /* Container card styling */
            .container-card {
                background-color: #2d2d2d; /* Slightly lighter dark for cards */
                padding: 1.5rem;
                border-radius: 10px;
                border: 1px solid #404040;
                height: 70vh; /* Set a fixed height for the cards */
                display: flex;
                flex-direction: column;
            }

            .chat-container {
                flex-grow: 1;
                overflow-y: auto; /* Make chat scrollable */
                padding-right: 1rem;
            }

            /* Custom chat bubbles */
            .chat-message {
                padding: 1rem 1.25rem; border-radius: 20px; margin-bottom: 1rem;
                display: flex; align-items: center; animation: fadeIn 0.5s ease-in-out;
            }
            .chat-message.user {
                background-color: #007bff; /* Bright blue for user */
                color: white; margin-left: auto; max-width: 75%; flex-direction: row-reverse;
            }
            .chat-message.assistant {
                background-color: #3b3b3b; /* Grey for AI messages */
                color: #e0e0e0; max-width: 75%;
            }
            .chat-message .avatar { 
                font-size: 24px; 
                margin-left: 15px; /* For user avatar on the right */
                margin-right: 15px; /* For assistant avatar on the left */
            }
            .chat-message .message { flex-grow: 1; font-size: 1rem; line-height: 1.6; }

            /* Status box in the control panel */
            .status-box {
                padding: 15px; border-radius: 10px; border-left: 5px solid;
                background-color: #3b3b3b;
            }
            .status-box.info { border-color: #007bff; }
            .status-box.success { border-color: #2ed573; }
            .status-box.warning { border-color: #ffa502; }
            .status-box p { font-weight: 600; color: #ffffff; }

            /* Final report styling */
            .final-report { padding: 1rem; border: 1px solid #404040; border-radius: 10px; }
            .final-report h3 { color: #007bff; border-bottom: none; }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    """, unsafe_allow_html=True)

load_css()

# --- Session State Initialization ---
if 'session_id' not in st.session_state: st.session_state.session_id = None
if 'messages' not in st.session_state: st.session_state.messages = []
if 'interview_state' not in st.session_state: st.session_state.interview_state = "NOT_STARTED"
if 'current_question' not in st.session_state: st.session_state.current_question = ""
if 'question_count' not in st.session_state: st.session_state.question_count = 0
if 'all_rounds_data' not in st.session_state: st.session_state.all_rounds_data = []

# --- Helper Functions for Display ---
def display_chat_message(role, content):
    avatar_emoji = "👤" if role == "user" else "🤖"
    # The order of avatar and message is swapped for the 'user' role via flex-direction in CSS
    st.markdown(f"""
        <div class="chat-message {role}">
            <div class="avatar">{avatar_emoji}</div>
            <div class="message">{content}</div>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.get('latest_audio'):
        voice.autoplay_audio(st.session_state.latest_audio)
        st.session_state.latest_audio = None

def display_status(icon, text, type="info"):
    st.markdown(f"""
        <div class="status-box {type}">
            <p>{icon} {text}</p>
        </div>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("💼 ProVoice AI")
    st.markdown("Your personal interview coach.")
    
    st.header("1. Configuration")
    job_role_input = st.text_input("Job Role", value="AI/ML Engineer")
    num_questions_input = st.number_input("Number of Questions", min_value=1, max_value=10, value=3)

    if st.button("🚀 Start New Interview", use_container_width=True, disabled=(st.session_state.interview_state == "IN_PROGRESS")):
        st.session_state.messages = []
        st.session_state.session_id = db.create_interview_session(job_role_input)
        st.session_state.question_count = 0
        st.session_state.all_rounds_data = []
        st.session_state.interview_state = "GENERATING_QUESTION"
        st.rerun()

    st.header("2. Interview History")
    past_sessions = db.get_all_sessions()
    if past_sessions:
        session_options = {f"ID {s[0]}: {s[1]} ({s[2]})": s[0] for s in past_sessions}
        selected_session_str = st.selectbox("Review a past session:", options=session_options.keys())
        
        if st.button("📖 Load Session", use_container_width=True):
            session_id_to_load = session_options[selected_session_str]
            rounds = db.get_rounds_for_session(session_id_to_load)
            st.session_state.messages = []
            st.session_state.interview_state = "REVIEWING"
            for q_num, (q, a, e) in enumerate(rounds):
                st.session_state.messages.append({'role': 'assistant', 'content': f"**Question {q_num+1}:** {q}"})
                st.session_state.messages.append({'role': 'user', 'content': a})
                st.session_state.messages.append({'role': 'assistant', 'content': f"**Feedback:** {e}"})

# --- MAIN CONTENT AREA ---
col1, col2 = st.columns([2, 1.2])

# Column 1: Chat History
with col1:
    st.markdown('<div class="container-card">', unsafe_allow_html=True)
    st.subheader("Conversation Transcript")
    
    with st.container(height=550): # Use Streamlit's built-in container with height for scrolling
        for message in st.session_state.messages:
            if "Final Report" in message['content']:
                report_content = message['content'].split('\n\n', 1)[1] if '\n\n' in message['content'] else message['content']
                st.markdown(f'<div class="final-report"><h3>📝 Final Performance Report</h3>{report_content}</div>', unsafe_allow_html=True)
            else:
                display_chat_message(message["role"], message["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)

# Column 2: Control Panel & Status
with col2:
    st.markdown('<div class="container-card">', unsafe_allow_html=True)
    st.subheader("Control Panel")
    
    status_box = st.container()
    recorder_placeholder = st.container()
    
    # --- State Machine Logic ---
    if st.session_state.interview_state == "NOT_STARTED" or st.session_state.interview_state == "REVIEWING":
        with status_box:
            display_status("👋", "Welcome! Start a new interview from the sidebar.")

    elif st.session_state.interview_state == "GENERATING_QUESTION":
        with status_box:
            display_status("🧠", "AI is preparing the next question...")
        
        if st.session_state.question_count == 0:
            question = ai.generate_initial_question(job_role_input)
        else:
            last_answer = st.session_state.all_rounds_data[-1]['answer']
            question = ai.generate_next_question(last_answer)

        st.session_state.current_question = question
        audio_bytes = voice.text_to_audio_bytes(question)
        st.session_state.messages.append({"role": "assistant", "content": question})
        st.session_state.latest_audio = audio_bytes
        st.session_state.interview_state = "WAITING_FOR_USER"
        st.rerun()

    elif st.session_state.interview_state == "WAITING_FOR_USER":
        with status_box:
            display_status("🎙️", "Your turn! Please record your answer below.", type="success")
        with recorder_placeholder:
            audio_info = mic_recorder(start_prompt="🔴 Start Recording", stop_prompt="⏹️ Stop Recording", key='recorder')
        
        if audio_info and audio_info['bytes']:
            st.session_state.audio_bytes = audio_info['bytes']
            st.session_state.interview_state = "PROCESSING_ANSWER"
            st.rerun()

    elif st.session_state.interview_state == "PROCESSING_ANSWER":
        with status_box:
            display_status("⏳", "Processing your answer...", type="warning")
        
        user_answer_text = voice.audio_bytes_to_text(st.session_state.audio_bytes)
        if user_answer_text:
            st.session_state.messages.append({"role": "user", "content": user_answer_text})
            
            evaluation = ai.evaluate_answer(st.session_state.current_question, user_answer_text)
            audio_bytes = voice.text_to_audio_bytes(f"Feedback: {evaluation}")
            st.session_state.messages.append({"role": "assistant", "content": f"**Feedback:** {evaluation}"})
            st.session_state.latest_audio = audio_bytes
            
            st.session_state.all_rounds_data.append({
                "question": st.session_state.current_question, "answer": user_answer_text, "evaluation": evaluation
            })
            db.save_round(st.session_state.session_id, st.session_state.current_question, user_answer_text, evaluation)
            st.session_state.question_count += 1
            
            if st.session_state.question_count < num_questions_input:
                st.session_state.interview_state = "GENERATING_QUESTION"
            else:
                st.session_state.interview_state = "GENERATING_REPORT"
        else:
            with status_box:
                display_status("⚠️", "Could not understand audio. Let's try again.", type="warning")
            st.session_state.messages.append({"role": "assistant", "content": "I couldn't catch that. Please try recording that answer again."})
            st.session_state.interview_state = "WAITING_FOR_USER"
        
        st.rerun()

    elif st.session_state.interview_state == "GENERATING_REPORT":
        with status_box:
            display_status("📑", "Interview complete! Generating final report...")
        final_report = ai.generate_final_report(st.session_state.all_rounds_data)
        
        audio_bytes = voice.text_to_audio_bytes("Your interview is complete. Here is the final report.")
        st.session_state.messages.append({"role": "assistant", "content": f"### Final Report\n\n{final_report}"})
        st.session_state.latest_audio = audio_bytes
        st.session_state.interview_state = "FINISHED"
        st.rerun()

    elif st.session_state.interview_state == "FINISHED":
        with status_box:
            display_status("✅", "Interview Finished! Review the report and start a new session from the sidebar.", type="success")

    st.markdown('</div>', unsafe_allow_html=True)