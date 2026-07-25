import string


# =====================================================
# Helper Functions
# =====================================================

def normalize(answer):
    """
    Normalize answers before comparison.
    """

    answer = answer.strip().lower()

    # Remove punctuation
    answer = "".join(
        c for c in answer
        if c not in string.punctuation
    )

    # Remove extra spaces
    answer = " ".join(answer.split())

    return answer


def exact_match(student, reference):
    """
    Exact string comparison.
    """

    return student == reference


def numerical_match(student, reference):
    """
    Compare numerical answers.
    """

    try:
        return float(student) == float(reference)

    except ValueError:
        return False


def keyword_match(student, reference):
    """
    Accept answers containing the reference.
    """

    return reference in student


def multiple_answers(student, references):
    """
    Support multiple acceptable answers.
    """

    for answer in references:

        if normalize(answer) == student:
            return True

    return False


def unit_match(student, reference):
    """
    Placeholder for unit comparison.
    """

    student = student.split()
    reference = reference.split()

    if len(student) != 2:
        return False

    if len(reference) != 2:
        return False

    return student[1] == reference[1]


# =====================================================
# Determine Correctness
# =====================================================

def evaluate_answer(student, reference):

    # -----------------------------------
    # Multiple correct answers
    # -----------------------------------

    if isinstance(reference, list):

        if multiple_answers(student, reference):

            return {
                "correct": True,
                "score_ratio": 1.0,
                "method": "Alternative Answer",
                "reason": "Student used an accepted alternative answer."
            }

        return {
            "correct": False,
            "score_ratio": 0.0,
            "method": "No Match",
            "reason": "Student answer is not one of the accepted answers."
        }

    # -----------------------------------
    # Numerical comparison
    # -----------------------------------

    if numerical_match(student, reference):

        return {
            "correct": True,
            "score_ratio": 1.0,
            "method": "Numerical Match",
            "reason": "Numerical values are equal."
        }

    # -----------------------------------
    # Exact comparison
    # -----------------------------------

    if exact_match(student, reference):

        return {
            "correct": True,
            "score_ratio": 1.0,
            "method": "Exact Match",
            "reason": "Answers are identical."
        }

    # -----------------------------------
    # Keyword comparison
    # -----------------------------------

    if keyword_match(student, reference):

        return {
            "correct": True,
            "score_ratio": 0.75,
            "method": "Keyword Match",
            "reason": "Reference answer appears inside the student's answer."
        }

    # -----------------------------------
    # No match
    # -----------------------------------

    return {
        "correct": False,
        "score_ratio": 0.0,
        "method": "No Match",
        "reason": "Answers do not match."
    }


# =====================================================
# Grade One Question
# =====================================================

def grade(question):

    # -----------------------------------
    # Prepare answers
    # -----------------------------------

    student = normalize(question["student_answer"])

    reference = question["reference_answer"]

    if isinstance(reference, str):
        reference = normalize(reference)

    print("--------------------------------")
    print("Student:", student)
    print("Reference:", reference)

    # -----------------------------------
    # Evaluate answer
    # -----------------------------------

    evaluation = evaluate_answer(student, reference)

    score = question["marks"] * evaluation["score_ratio"]

    # -----------------------------------
    # Return grading result
    # -----------------------------------

    return {

        "question": question["question"],

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


# =====================================================
# Grade Entire Exam
# =====================================================

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