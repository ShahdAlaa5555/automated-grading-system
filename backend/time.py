import time

print("Sending prompt to Qwen...")

start = time.time()

response = chat(
    model=MODEL,
    think=False,
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print("LLM finished in", time.time() - start, "seconds")