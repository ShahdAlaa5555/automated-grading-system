# ir.py

import json

def build_ir(clean_text, diagram_json):

    diagram = json.loads(diagram_json)

    ir = {
        "student_text": clean_text,
        "diagram": diagram
    }

    return ir