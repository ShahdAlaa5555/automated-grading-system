from expression_grader import evaluate_expression

tests = [

    ("2*(x+3)", "2*x+3"),

    ("x**2-1", "(x-1)*(x+1)"),

    ("2/4", "1/2"),

    ("sqrt(8)", "2*sqrt(2)"),

    ("2*x+5", "2*x+6")

]

for student, reference in tests:

    result = evaluate_expression(student, reference)

    print("--------------------------------")
    print("Student  :", student)
    print("Reference:", reference)
    print(result)