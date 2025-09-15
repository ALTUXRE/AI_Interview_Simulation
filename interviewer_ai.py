# interviewer_ai.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
try:
    genai.configure(api_key=os.getenv("AIzaSyBa7N9ITEqgURBoLPePH6EeX_a7hvGJo_w"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"Error configuring Gemini API: {e}")
    model = None

# Store conversation history in memory for the current session
conversation_history = []

def generate_initial_question(job_role):
    """Generates the first question for the interview."""
    if not model: return "AI model not configured. Please check your API key."
    
    global conversation_history
    conversation_history = [] # Reset history for a new interview
    
    prompt = f"You are an expert interviewer conducting an interview for a '{job_role}' position. Your tone is professional and encouraging. Start by briefly introducing yourself and then ask me the first relevant technical or behavioral question. Keep your questions clear and concise."
    
    response = model.generate_content(prompt)
    conversation_history.append({'role': 'model', 'parts': [response.text]})
    return response.text

def generate_next_question(user_answer):
    """Generates a follow-up question based on the conversation history."""
    if not model: return "AI model not configured."
    
    global conversation_history
    conversation_history.append({'role': 'user', 'parts': [user_answer]})
    
    # The prompt guides the AI to ask the next question logically
    prompt = "That was the candidate's answer. Based on our conversation so far, ask the next logical question. Do not repeat questions."
    
    # Start a chat with the existing history
    chat = model.start_chat(history=conversation_history)
    response = chat.send_message(prompt)
    
    conversation_history.append({'role': 'model', 'parts': [response.text]})
    return response.text

def evaluate_answer(question, user_answer):
    """Evaluates the user's answer and provides a score and feedback."""
    if not model: return "AI model not configured."

    prompt = f"""
    As an expert interviewer, please evaluate the following answer provided for a specific question.
    Provide a score from 1 to 10 and a brief, constructive justification for your score. Focus on clarity, relevance to the question, and accuracy.

    Question: "{question}"
    Candidate's Answer: "{user_answer}"

    Your Evaluation (Score and Justification):
    """
    response = model.generate_content(prompt)
    return response.text

def generate_final_report(all_rounds_data):
    """Generates a summary report of the entire interview."""
    if not model: return "AI model not configured."

    evaluations_text = "\n\n".join(
        f"Question: {r['question']}\nAnswer: {r['answer']}\nEvaluation: {r['evaluation']}" 
        for r in all_rounds_data
    )
    
    prompt = f"""
    Based on the following interview transcript and individual evaluations, please provide a final summary of the candidate's performance.
    Conclude by highlighting their key strengths and suggesting 2-3 specific areas for improvement.

    Interview Transcript & Evaluations:
    {evaluations_text}

    Final Performance Summary:
    """
    response = model.generate_content(prompt)
    return response.text