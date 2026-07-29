from grading_utils import numerical_match


def evaluate_numerical(student, reference):

    if numerical_match(student, reference):

        return {
            "correct": True,
            "score_ratio": 1.0,
            "method": "Numerical Match",
            "reason": "Numerical values are equal."
        }

    return {
        "correct": False,
        "score_ratio": 0.0,
        "method": "No Match",
        "reason": "Numbers are different."
    }