from grading_utils import (
    exact_match,
    keyword_match,
    multiple_answers
)


def evaluate_text(student, reference):

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
            "reason": "Student answer is not accepted."
        }


    if exact_match(student, reference):

        return {
            "correct": True,
            "score_ratio": 1.0,
            "method": "Exact Match",
            "reason": "Answers are identical."
        }


    if keyword_match(student, reference):

        return {
            "correct": True,
            "score_ratio": 0.75,
            "method": "Keyword Match",
            "reason": "Reference answer appears inside student's answer."
        }


    return {
        "correct": False,
        "score_ratio": 0.0,
        "method": "No Match",
        "reason": "Answers do not match."
    }