from ocr_with_qwen_cleaner import read_image
from qwen import repair
from diagram_understanding import analyse_diagram
from intermediate import build_ir
from grader import grade_answer

###################################################
# INPUT IMAGE
###################################################

image = "examq2.png"

###################################################
# OCR
###################################################

raw = read_image(image)

print("\n================ RAW OCR ================\n")
print(raw)

###################################################
# OCR REPAIR
###################################################

clean = repair(image, raw)

print("\n================ REPAIRED OCR ================\n")
print(clean)

###################################################
# DIAGRAM UNDERSTANDING
###################################################

diagram = analyse_diagram(image)

print("\n================ DIAGRAM ================\n")
print(diagram)

###################################################
# INTERMEDIATE REPRESENTATION
###################################################

ir = build_ir(

    clean,

    diagram,

    subject="math",

    question_number=10

)

print("\n================ IR ================\n")
print(ir)

###################################################
# GRADING
###################################################

grade = grade_answer(ir)

###################################################
# RESULT
###################################################

print()

print("=" * 60)
print("FINAL GRADE")
print("=" * 60)
print(grade)