import ollama
import base64

# Load image and convert to base64
with open('D:\\grading_project\\test_images\\bio_diagram.jpg', 'rb') as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Send to LLaVA
print("Sending to LLaVA...")
response = ollama.chat(
    model='llava',
    messages=[{
        'role': 'user',
        'content': """You are a biology teacher grading a student exam.
        
Look at this biology diagram carefully.

The student was asked: "Describe what this diagram shows and identify the key components."

The student answered: "This shows a plant cell with a cell wall and chloroplasts."

Grade the student's answer 0-3:
0 = completely wrong or blank
1 = partially correct, missing key observations  
2 = mostly correct, minor gap
3 = fully correct and complete

Reply in this format:
Image shows: [what you see in the diagram]
Score: [0-3]/3
Thinking: [your reasoning]
Feedback: [2 sentences in German to the student]""",
        'images': [image_data]
    }]
)

print("\n=== LLAVA RESULT ===")
print(response['message']['content'])