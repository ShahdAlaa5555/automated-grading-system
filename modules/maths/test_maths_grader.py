from maths_grader import grade_exam

exam = [

    # ----------------------------
    # Exact Match
    # ----------------------------
    {
        "question": "Capital of France",
        "marks": 2,
        "reference_answer": "Paris",
        "student_answer": "Paris"
    },

    # ----------------------------
    # Numerical Match
    # ----------------------------
    {
        "question": "2 + 2",
        "marks": 2,
        "reference_answer": "4",
        "student_answer": "4.0"
    },

    # ----------------------------
    # Keyword Match
    # ----------------------------
    {
        "question": "Capital of France",
        "marks": 2,
        "reference_answer": "Paris",
        "student_answer": "The answer is Paris."
    },

    # ----------------------------
    # Alternative Answer
    # ----------------------------
    {
        "question": "British or American spelling",
        "marks": 2,
        "reference_answer": ["centre", "center"],
        "student_answer": "center"
    },

    # ----------------------------
    # Wrong Answer
    # ----------------------------
    {
        "question": "5 × 5",
        "marks": 2,
        "reference_answer": "25",
        "student_answer": "30"
    }

]

result = grade_exam(exam)

print(result)