import tempfile
import streamlit as st
from PIL import Image

from ocr_with_qwen_cleaner import read_image
from qwen import repair

st.set_page_config(
    page_title="OCR + Qwen",
    layout="wide"
)

st.title("OCR + Qwen Pipeline")

uploaded = st.file_uploader(
    "Upload a student's answer",
    type=["png", "jpg", "jpeg"]
)

if uploaded is not None:

    # Display the uploaded image
    image = Image.open(uploaded)

    st.subheader("Original Image")
    st.image(image, use_container_width=True)

    # Save uploaded image temporarily because
    # EasyOCR and Ollama expect a file path
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".png"
    ) as tmp:

        image.save(tmp.name)
        image_path = tmp.name

    if st.button("Run OCR + Qwen"):

        with st.spinner("Running OCR..."):
            raw = read_image(image_path)

        st.subheader("Raw OCR")

        st.text_area(
            "OCR Output",
            raw,
            height=250
        )

        with st.spinner("Repairing with Qwen..."):
            repaired = repair(image_path, raw)

        st.subheader("Qwen Repaired")

        st.text_area(
            "Cleaned Output",
            repaired,
            height=350
        )