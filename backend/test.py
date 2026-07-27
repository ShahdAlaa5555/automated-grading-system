from ollama import chat

print("Before chat")

response = chat(
    model="qwen3:4b",
    messages=[
        {
            "role": "user",
            "content": "Say hello."
        }
    ]
)

print("After chat")
print(response)