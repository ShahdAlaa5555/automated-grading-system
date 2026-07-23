#This reads an image and returns the text in it by using EasyOCR. Then, it uses Qwen to repair the answer as closely as possible to what the student actually wrote.
# from llm import read_image
from qwen import repair
import easyocr

reader = easyocr.Reader(["en"])

def read_image(path):
    result = reader.readtext(path, detail=0)

    text = "\n".join(result)

    return text

# 

# -----------------------------
# Only runs when you execute this file directly
# -----------------------------
if __name__ == "__main__":

    image = "exam_images/examq10.png"

    raw = read_image(image)

    print("=" * 60)
    print("RAW OCR")
    print("=" * 60)
    print(raw)

    clean = repair(image, raw)

    print("=" * 60)
    print("QWEN REPAIRED")
    print("=" * 60)
    print(clean)