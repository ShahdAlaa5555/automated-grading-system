import string
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
