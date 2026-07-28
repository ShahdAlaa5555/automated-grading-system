from ocr_with_qwen_cleaner import read_image
from qwen import repair
from diagram_understanding import analyse_diagram
from intermediate import build_ir
from grader import grade_answer


def grade_question_image(image_path):

    ###################################################
    # OCR
    ###################################################

    raw = read_image(image_path)

    ###################################################
    # OCR Repair
    ###################################################

    clean = repair(image_path, raw)

    ###################################################
    # Diagram Understanding
    ###################################################

    diagram = analyse_diagram(image_path)

    ###################################################
    # Intermediate Representation
    ###################################################

    ir = build_ir(

        clean,

        diagram,

        subject="math",

        question_number=1

    )

    ###################################################
    # Grade
    ###################################################

    return grade_answer(ir)