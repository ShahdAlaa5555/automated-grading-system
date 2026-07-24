from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

# Load model only once
model = SentenceTransformer("all-MiniLM-L6-v2")


def grade(correct_answer, student_answer, max_marks=5):
    emb1 = model.encode(correct_answer, convert_to_tensor=True)
    emb2 = model.encode(student_answer, convert_to_tensor=True)

    similarity = cos_sim(emb1, emb2).item()

    marks = round(similarity * max_marks)

    # Keep marks within range
    marks = max(0, min(max_marks, marks))

    return similarity, marks


# ==========================================
# Test Cases
# ==========================================

tests = [
    {
        "title": "Exact Answer",
        "correct": "An ionic bond is the electrostatic attraction between oppositely charged ions.",
        "student": "An ionic bond is the electrostatic attraction between oppositely charged ions."
    },

    {
        "title": "Same Meaning",
        "correct": "An ionic bond is the electrostatic attraction between oppositely charged ions.",
        "student": "It is the attraction between positive and negative ions."
    },

    {
        "title": "Partially Correct",
        "correct": "An ionic bond is the electrostatic attraction between oppositely charged ions.",
        "student": "It is a chemical bond between atoms."
    },

    {
        "title": "Wrong Answer",
        "correct": "An ionic bond is the electrostatic attraction between oppositely charged ions.",
        "student": "Photosynthesis occurs in plant leaves."
    },

    {
        "title": "Very Short",
        "correct": "An ionic bond is the electrostatic attraction between oppositely charged ions.",
        "student": "Ionic bond."
    },

    {
        "title": "Water Boiling",
        "correct": "Water boils at 100 degrees Celsius.",
        "student": "The boiling point of water is 100°C."
    },

    {
        "title": "Water Wrong",
        "correct": "Water boils at 100 degrees Celsius.",
        "student": "Water freezes at 0 degrees Celsius."
    },

    {
        "title": "Definition",
        "correct": "An acid is a substance that donates hydrogen ions.",
        "student": "An acid releases H+ ions in solution."
    },

    {
        "title": "Definition Wrong",
        "correct": "An acid is a substance that donates hydrogen ions.",
        "student": "An acid is a type of metal."
    }
]

# ==========================================
# Run Tests
# ==========================================

print("=" * 80)
print("CHEMISTRY AI GRADING TEST")
print("=" * 80)

for i, test in enumerate(tests, start=1):

    similarity, marks = grade(
        test["correct"],
        test["student"]
    )

    print(f"\nTest {i}: {test['title']}")
    print("-" * 80)
    print("Correct Answer:")
    print(test["correct"])
    print()

    print("Student Answer:")
    print(test["student"])
    print()

    print(f"Similarity : {similarity:.3f}")
    print(f"Marks      : {marks}/5")

print("\n" + "=" * 80)