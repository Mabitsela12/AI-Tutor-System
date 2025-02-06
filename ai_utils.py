# searchapp/ai_utils.py
import openai

openai.api_key = "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"

def generate_search_query(question):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": f"Generate a YouTube search query for the following question: {question}"}]
    )
    return response['choices'][0]['message']['content'].strip()
