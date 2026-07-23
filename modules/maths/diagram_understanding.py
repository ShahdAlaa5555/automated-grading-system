# diagram_understanding.py

import ollama

DIAGRAM_PROMPT = """
You are NOT describing the image.

You are extracting every visible component of the diagram.

For every diagram, identify:

1. Diagram type.

2. Every axis.

3. Every axis label.

4. Every tick mark.

5. Every tick value.

6. Every category label.

7. Every bar, line, point, sector or shape.

8. The approximate coordinates of each object relative to the axes.

Never summarize.

Never interpret.

Never compute values from the graph.

Never answer the exam question.

Return JSON only.
"""

# 
import ollama

def analyse_diagram(image_path):

    response = ollama.chat(
        model="qwen2.5vl:3b",
        messages=[
            {
                "role": "system",
                "content": DIAGRAM_PROMPT
            },
            {
                "role": "user",
                "content": "Describe only the diagrams in this image.",
                "images": [image_path]
            }
        ]
    )

    return response["message"]["content"]