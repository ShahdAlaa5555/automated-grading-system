from pdf2image import convert_from_path
import os

def pdf_to_images(pdf_path, output_folder="temp_images"):
    os.makedirs(output_folder, exist_ok=True)

    pages = convert_from_path(pdf_path, dpi=300)

    image_paths = []

    for i, page in enumerate(pages):
        image_path = os.path.join(output_folder, f"page_{i+1}.jpg")
        page.save(image_path, "JPEG")
        image_paths.append(image_path)

    return image_paths