import sys
import os
os.environ['HF_HOME'] = 'D:\\hf_cache'
sys.path.insert(0, 'D:\\Python312\\Lib\\site-packages')

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
import torch
import cv2
import numpy as np

# Load model
print("Loading TrOCR model...")
processor = TrOCRProcessor.from_pretrained('microsoft/trocr-large-handwritten')
model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-large-handwritten')
print("Model loaded!")

def extract_lines(image_path):
    """Use OpenCV to detect and crop individual lines from handwritten page."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Threshold to get binary image
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)
    
    # Dilate horizontally to connect letters in same line
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 3))
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    
    # Find contours of each line
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Sort contours top to bottom
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])
    
    lines = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        # Filter out very small contours (noise)
        if h > 15 and w > 50:
            # Add padding around each line
            pad = 10
            y1 = max(0, y - pad)
            y2 = min(img.shape[0], y + h + pad)
            line_img = img[y1:y2, :]
            lines.append(line_img)
    
    return lines

def read_line(line_img):
    """Run TrOCR on a single line image."""
    # Convert OpenCV image to PIL
    pil_img = Image.fromarray(cv2.cvtColor(line_img, cv2.COLOR_BGR2RGB))
    
    pixel_values = processor(images=pil_img, return_tensors='pt').pixel_values
    
    with torch.no_grad():
        generated_ids = model.generate(
            pixel_values,
            max_new_tokens=100
        )
    
    text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return text

# Process image
image_path = 'D:\\grading_project\\test_images\\test1.jpeg'
print("Detecting lines...")
lines = extract_lines(image_path)
print(f"Found {len(lines)} lines")

print("\n=== TrOCR RESULTS ===")
full_text = []
for i, line_img in enumerate(lines):
    text = read_line(line_img)
    print(f"Line {i+1}: {text}")
    full_text.append(text)

print("\n=== FULL TEXT ===")
print('\n'.join(full_text))