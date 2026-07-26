from grading_utils import normalize
from text_grader import evaluate_text
from numerical_grader import evaluate_numerical
from expression_grader import evaluate_expression


def evaluate_question(question):

    student = question["student_answer"]
    reference = question["reference_answer"]

    question_type = question.get("type", "text")

    if question_type != "expression":
        student = normalize(student)

    if isinstance(reference, str):
        reference = normalize(reference)

    # -----------------------------
    # Dispatch to the correct grader
    # -----------------------------

    if question_type == "text":
        return evaluate_text(student, reference)

    if question_type == "numerical":
        return evaluate_numerical(student, reference)

    if question_type == "expression":
        return evaluate_expression(student, reference)

    return {
        "correct": False,
        "score_ratio": 0,
        "method": "Unsupported",
        "reason": "Unsupported question type."
    }
def grade(question):

    # -----------------------------------
    # Evaluate the question
    # -----------------------------------

    evaluation = evaluate_question(question)

    score = question["marks"] * evaluation["score_ratio"]

    # -----------------------------------
    # Return grading result
    # -----------------------------------

    return {

        "question": question["question"],

        "type": question["type"],

        "student_answer": question["student_answer"],

        "reference_answer": question["reference_answer"],

        "correct": evaluation["correct"],

        "method": evaluation["method"],

        "score": score,

        "max_score": question["marks"],

        "feedback": (
            "Correct."
            if evaluation["correct"]
            else "Incorrect."
        ),

        "reason": evaluation["reason"]

    }
def grade_exam(exam):

    results = []

    total_score = 0
    total_marks = 0

    for question in exam:

        result = grade(question)

        results.append(result)

        total_score += result["score"]
        total_marks += result["max_score"]

    return {

        "questions": results,

        "total_score": total_score,

        "total_marks": total_marks

    }