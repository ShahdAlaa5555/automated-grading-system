import sys
sys.path.insert(0, 'D:\\grading_project\\libs')
import easyocr
import cv2
import numpy as np 


reader= easyocr.Reader(['de','en'])
image_path = 'D:\\grading_project\\test_images\\test1.jpeg'

image=cv2.imread(image_path)
gray= cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
denoised = cv2.fastNlMeansDenoising(gray, h=10)
thresh = cv2.adaptiveThreshold(denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
results = reader.readtext(thresh)
print("\n=== OCR RESULTS ===")
for (bbox, text, confidence) in results:
    print(f"Text: {text}")
    print(f"Confidence: {round(confidence * 100, 1)}%")
    print("---")

full_text = " ".join([text for (bbox, text, confidence) in results])
print("\n=== FULL EXTRACTED TEXT ===")
print(full_text)