from maths_grader import grade_exam

exam = [

    # ----------------------------
    # Exact Match
    # ----------------------------
    {
        "question": "Capital of France",
        "type": "text",
        "marks": 2,
        "reference_answer": "Paris",
        "student_answer": "Paris"
    },

    # ----------------------------
    # Numerical Match
    # ----------------------------
    {
        "question": "2 + 2",
        "type": "text",
        "marks": 2,
        "reference_answer": "4",
        "student_answer": "4.0"
    },

    # ----------------------------
    # Keyword Match
    # ----------------------------
    {
        "question": "Capital of France",
        "type": "text",
        "marks": 2,
        "reference_answer": "Paris",
        "student_answer": "The answer is Paris."
    },

    # ----------------------------
    # Alternative Answer
    # ----------------------------
    {
        "question": "British or American spelling",
        "type": "text",
        "marks": 2,
        "reference_answer": ["centre", "center"],
        "student_answer": "center"
    },

    # ----------------------------
    # Wrong Answer
    # ----------------------------
    {
        "question": "5 × 5",
        "type": "numerical",
        "marks": 2,
        "reference_answer": "25",
        "student_answer": "30"
    },
    {
    "question":"???",

    "type":"banana",

    "marks":2,

    "reference_answer":"5",

    "student_answer":"5"
},
{
    "question":"Spelling",

    "type":"text",

    "marks":2,

    "reference_answer":[
        "centre",
        "center"
    ],

    "student_answer":"center"
},
{
    "question": "Expand",
    "type": "expression",
    "marks": 4,
    "reference_answer": "2*x + 6",
    "student_answer": "2*x + 5"
}
]

result = grade_exam(exam)

print(result)