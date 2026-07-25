from ocr import extract_text   # replace "ocr" with your filename if different

lines = run_pipeline()

print("\n========== FINAL TEXT ==========\n")

for line in lines:
    print(line)