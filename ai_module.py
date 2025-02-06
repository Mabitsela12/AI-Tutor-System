import openai

# Set your OpenAI API key here
openai.api_key = "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"

# Function to generate quiz questions using OpenAI for a specific subject and grade
def generate_quiz_for_subject(subject, grade):
    prompt = f"Generate 3  multiple-choice quiz questions for the subject '{subject}' for Grade {grade}. Each question should have 4 options labeled A, B, C, D. Clearly indicate the correct answer."
    
    try:
        # Query the OpenAI API to generate quiz questions
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates educational content."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        content = response['choices'][0]['message']['content'].strip()
        return parse_quiz_from_response(content)  # Parse the AI-generated response
    except Exception as e:
        return {"error": str(e)}


# Function to parse the AI's response into a structured quiz format
def parse_quiz_from_response(response):
    quiz = []
    questions = response.split('\n\n')  # Adjust the splitting based on AI response format

    for question in questions:
        lines = question.split('\n')
        if len(lines) >= 5:  # Ensure you have at least 5 lines (1 question + 4 options)
            question_text = lines[0].strip()  # The question text
            options = [line.strip() for line in lines[1:5]]  # Options A, B, C, D
            answer_line = next((line for line in lines if "answer" in line.lower()), None)  # Look for "answer"
            answer = answer_line.split(":")[-1].strip() if answer_line else "N/A"  # Extract the correct answer
            
            quiz.append({
                "question": question_text,
                "options": options,
                "correct_answer": answer,
            })
    
    return quiz

# Example of checking answers (with an AI-generated quiz)
def check_answers(selected_answers, quiz):
    correct_count = 0
    for question in quiz:
        if selected_answers.get(question["question"]) == question["correct_answer"]:
            correct_count += 1
    return correct_count
