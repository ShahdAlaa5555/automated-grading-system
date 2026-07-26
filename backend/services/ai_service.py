import os
from dotenv import load_dotenv
from google import genai

# Load the .env file
load_dotenv()

# Create the Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

def grade_chemistry(text):

    prompt = f"""
You are an experienced German chemistry teacher.

Read the following student's chemistry exam.

Provide:
1. Overall grade out of 100.
2. Feedback.
3. Main strengths.
4. Main weaknesses.

Student Exam:

{text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return {
        "result": response.text
    }