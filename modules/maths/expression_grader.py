from sympy import simplify
from sympy.parsing.sympy_parser import parse_expr
def evaluate_expression(student, reference):

    try:

        student_expr = parse_expr(student)

        reference_expr = parse_expr(reference)

        difference = simplify(student_expr - reference_expr)

        if difference == 0:

            return {
                "correct": True,
                "score_ratio": 1.0,
                "method": "Symbolic Match",
                "reason": "Expressions are mathematically equivalent."
            }

    except Exception:

        pass
    return {

        "correct": False,

        "score_ratio": 0,

        "method": "Expression Mismatch",

        "reason": "Expressions are not equivalent."

    }
