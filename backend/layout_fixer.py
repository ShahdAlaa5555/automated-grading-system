def fix_layout(text):
    lines = text.splitlines()

    cleaned = []

    for line in lines:
        line = line.strip()

        if line == "":
            continue

        cleaned.append(line)

    return "\n".join(cleaned)