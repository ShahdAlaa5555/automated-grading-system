from ollama import chat

response = chat(
    model="qwen3:4b",
    format="json",
    messages=[
        {
            "role": "user",
            "content": """
Return ONLY this JSON:

{
    "name":"Max"
}
"""
        }
    ]
)

print(response["message"]["content"])