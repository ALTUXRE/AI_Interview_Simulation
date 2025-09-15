# main.py

import interviewer_ai as ai
import voice_interface as vi
import database as db
import time

def run_interview():
    """Main function to orchestrate the interview simulation."""
    
    # Initialize the database
    db.init_db()

    # --- Configuration ---
    job_role = input("Enter the job role you are interviewing for (e.g., Python Developer): ")
    try:
        num_questions = int(input("How many questions would you like to be asked? (e.g., 5): "))
    except ValueError:
        print("Invalid number. Defaulting to 3 questions.")
        num_questions = 3

    # --- Start of Interview ---
    print("\n--- Starting Interview Simulation ---")
    session_id = db.create_interview_session(job_role)
    all_rounds_data = []

    # Ask the first question
    vi.speak("Hello! Thank you for your interest. Let's begin the interview.")
    time.sleep(1)
    question = ai.generate_initial_question(job_role)
    
    for i in range(num_questions):
        vi.speak(question)
        
        # Listen for the user's answer
        user_answer = vi.listen()
        
        if not user_answer:
            vi.speak("It seems there was an issue with the audio. Let's move to the next question.")
            evaluation = "Skipped due to audio input error."
        else:
            # Evaluate the answer in real-time
            print("\nEvaluating your answer...")
            evaluation = ai.evaluate_answer(question, user_answer)
            print(f"Feedback: {evaluation}")
            vi.speak("Thank you for your response.")
            time.sleep(1)

        # Save the round to the database and a local list
        db.save_round(session_id, question, user_answer, evaluation)
        all_rounds_data.append({
            "question": question,
            "answer": user_answer,
            "evaluation": evaluation
        })

        # Generate the next question (if not the last one)
        if i < num_questions - 1:
            print("\nGenerating next question...")
            question = ai.generate_next_question(user_answer)
        else:
            vi.speak("That was the final question.")

    # --- End of Interview & Final Report ---
    vi.speak("The interview is now complete. Please wait a moment while I generate your final feedback report.")
    print("\n--- Generating Final Performance Report ---")
    
    final_report = ai.generate_final_report(all_rounds_data)
    
    print("\n" + "="*50)
    print("   FINAL INTERVIEW REPORT")
    print("="*50)
    print(f"Job Role: {job_role}")
    print(f"Session ID: {session_id}")
    print("-"*50)
    print(final_report)
    print("="*50)
    
    vi.speak("Your feedback report has been generated and displayed on the screen. This concludes our session. Thank you!")

if __name__ == "__main__":
    if ai.model is None:
        print("Failed to start the application due to an API configuration error.")
    else:
        run_interview()