from ollama import chat

response= chat(
    model="llava",
    messages=[
        {
            "role": "user",
            "content": """You are analyzing a scanned exam page.

Answer ONLY these questions:

1. Does this page contain a table? (yes/no)
2. Does this page contain a diagram? (yes/no)
3. Does this page contain handwritten text? (yes/no)
4. Is the page rotated? (yes/no)
5. Are there multiple columns? (yes/no)

Return JSON only.""",
            "images": ["images/chemexam.png"]   # replace with your image path
        }
    ]                   
        
)

print(response["message"]["content"])