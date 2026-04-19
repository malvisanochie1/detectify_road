import streamlit as st
from ultralytics import YOLO
from PIL import Image
from collections import Counter
import numpy as np
import pandas as pd
import cv2

st.set_page_config(page_title="Detectify Road", layout="centered")

st.title("🚗 Detectify Road")
st.caption("AI-powered road object detection system using YOLOv8")
st.write(
    "Upload a road image and Detectify Road will automatically identify and "
    "analyze objects such as cars, pedestrians, and trucks using a deep "
    "learning model."
)

@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)

    img_array = np.array(image)

    results = model.predict(img_array, conf=0.25)

    annotated_frame = results[0].plot()
    annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

    st.image(annotated_frame, caption="Detected Objects", use_container_width=True)

    # --- Detection Summary ---
    boxes = results[0].boxes
    total = len(boxes)

    st.subheader("📊 Detection Summary")
    st.metric("Total Objects Detected", total)

    if total > 0:
        class_names = [model.names[int(cls)] for cls in boxes.cls]
        confidences = [float(conf) * 100 for conf in boxes.conf]

        # Per-class percentages
        counts = Counter(class_names)
        st.write("**Objects by class:**")
        cols = st.columns(min(len(counts), 4))
        for i, (cls_name, count) in enumerate(counts.most_common()):
            pct = (count / total) * 100
            cols[i % len(cols)].metric(cls_name, f"{pct:.2f}%")

        # Detail table
        df = pd.DataFrame({
            "Object": class_names,
            "Confidence (%)": [f"{c:.2f}%" for c in confidences]
        })
        df = df.sort_values("Confidence (%)", ascending=False).reset_index(drop=True)
        df.index += 1
        st.table(df)
    else:
        st.info("No objects detected in this image.")

st.markdown(
    """
    <style>
    .detectify-footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        font-size: 12px;
        padding: 6px 0;
        background-color: var(--background-color, #000000);
        z-index: 100;
    }
    .detectify-footer hr {
        margin: 0 auto 4px auto;
        width: 60%;
        border: none;
    }
    </style>
    <div class="detectify-footer">
        <hr />
        <div>A project submitted by Anyanti Alexander Chibueze</div>
        <div>AIT/HND/24/00011</div>
    </div>
    """,
    unsafe_allow_html=True,
)
