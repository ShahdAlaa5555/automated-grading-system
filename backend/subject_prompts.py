def get_parser_prompt(subject):

    if subject == "chemistry":

        return """
You are an expert German chemistry teacher.

Extract the complete chemistry exam from OCR.
"""

    elif subject == "math":

        return """
You are an expert German mathematics teacher.

Extract the complete mathematics exam from OCR.
"""

    elif subject == "biology":

        return """
You are an expert German biology teacher.

Extract the complete biology exam from OCR.
"""

    elif subject == "german":

        return """
You are an expert German language teacher.

Extract the complete German exam from OCR.
"""

    else:

        raise Exception("Unknown subject.")