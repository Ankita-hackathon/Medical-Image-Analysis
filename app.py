
import os
import time
from io import BytesIO
from datetime import datetime

import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ==========================================
# 1. LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

# ==========================================
# 2. PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediScan AI",
    page_icon="🩻",
    layout="wide"
)

# ==========================================
# 3. CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #071426, #102941);
    color: #edf5ff;
}

[data-testid="stSidebar"] {
    background: #091a2d;
}

.hero {
    padding: 25px;
    border: 1px solid #294761;
    border-radius: 18px;
    background: #102941;
    margin-bottom: 25px;
}

.hero h1 {
    color: #ffffff;
    font-size: 38px;
}

.hero p {
    color: #b7cde0;
    font-size: 16px;
}

.stButton button {
    background-color: #35bde0;
    color: white;
    border-radius: 10px;
    font-weight: bold;
    border: none;
}

.result-box {
    background: #102941;
    padding: 20px;
    border-radius: 15px;
    border: 1px solid #294761;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. APPLICATION HEADER
# ==========================================

st.markdown("""
<div class="hero">

<h1>🩻 MediScan AI</h1>

<p>Generative AI Medical Image Analysis Assistant</p>

<p>Upload • Analyze • Generate Reports</p>

</div>
""", unsafe_allow_html=True)

# ==========================================
# 5. SIDEBAR
# ==========================================

with st.sidebar:

    st.title("🩻 MediScan AI")

    st.write("Medical Image Analysis Dashboard")

    st.divider()

    modality = st.selectbox(
        "Select Image Type",
        ["X-ray", "CT Scan", "MRI", "Other"]
    )

    body_region = st.text_input(
        "Body Region",
        placeholder="Example: Chest"
    )

    report_style = st.selectbox(
        "Report Style",
        ["Simple", "Technical"]
    )

    st.divider()

    st.info(
        "Educational prototype only. "
        "Not intended for clinical diagnosis."
    )

# ==========================================
# 6. MAIN LAYOUT
# ==========================================

left, right = st.columns(2, gap="large")

# ==========================================
# 7. IMAGE UPLOAD SECTION
# ==========================================

with left:

    st.subheader("📤 Upload Medical Image")

    uploaded_file = st.file_uploader(
        "Upload your medical image",
        type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_file:

        try:

            preview = Image.open(
                BytesIO(uploaded_file.getvalue())
            ).convert("RGB")

            st.image(
                preview,
                caption="Uploaded Medical Image",
                use_container_width=True
            )

            st.success("Image uploaded successfully!")

        except Exception:

            st.error("Invalid image. Please upload another file.")

            uploaded_file = None

# ==========================================
# 8. AI ANALYSIS SECTION
# ==========================================

with right:

    st.subheader("🤖 AI Image Analysis")

    api_key = os.getenv(
        "GEMINI_API_KEY", ""
    ).strip()

    if not api_key:

        st.warning(
            "Gemini API key not found. "
            "Configure your .env file."
        )

    analyze_button = st.button(
        "🔍 Analyze Image",
        type="primary",
        use_container_width=True,
        disabled=(uploaded_file is None or not api_key)
    )

    if analyze_button:

        with st.spinner("⚡ AI is analyzing your image..."):

            try:

                start_time = time.time()

                # Initialize Gemini client
                client = genai.Client(
                    api_key=api_key
                )

                # ==================================
                # IMAGE PREPROCESSING
                # ==================================

                image = Image.open(
                    BytesIO(uploaded_file.getvalue())
                ).convert("RGB")

                original_width, original_height = image.size

                # Resize large image
                image.thumbnail((1600, 1600))

                image_buffer = BytesIO()

                image.save(
                    image_buffer,
                    format="JPEG",
                    quality=85,
                    optimize=True
                )

                image_data = image_buffer.getvalue()

                # ==================================
                # OPTIMIZED PROMPT
                # ==================================

                prompt = f"""
                Review this medical image for educational purposes.

                Modality: {modality}
                Body Region: {body_region or "Not specified"}
                Report Style: {report_style}

                Generate a concise report containing:

                1. Image Quality
                2. Visible Observations
                3. Features Requiring Professional Review
                4. Image Limitations
                5. Suggested Clinical Review Questions

                IMPORTANT:

                Do not diagnose or prescribe treatment.
                Do not invent image findings.
                Use cautious language.
                Mention uncertainty and limitations.
                Professional radiologist interpretation is required.
                """

                # ==================================
                # GEMINI IMAGE ANALYSIS
                # ==================================

                response = client.models.generate_content(

                    model="gemini-3.5-flash-lite",

                    contents=[

                        prompt,

                        types.Part.from_bytes(
                            data=image_data,
                            mime_type="image/jpeg"
                        )

                    ],

                    config=types.GenerateContentConfig(

                        max_output_tokens=400,

                        temperature=0.2

                    )
                )

                analysis = response.text

                if not analysis:

                    raise ValueError(
                        "Empty AI response received."
                    )

                # ==================================
                # SAVE ANALYSIS RESULTS
                # ==================================

                elapsed_time = round(
                    time.time() - start_time, 2
                )

                st.session_state["analysis"] = analysis

                st.session_state["filename"] = uploaded_file.name

                st.session_state["date"] = (
                    datetime.now().strftime(
                        "%d-%m-%Y %H:%M:%S"
                    )
                )

                st.session_state["elapsed"] = elapsed_time

                st.session_state["image_dimensions"] = (
                    original_width, original_height
                )

                st.success(
                    f"Analysis completed in {elapsed_time} seconds!"
                )

            except Exception as e:

                st.error(
                    f"Analysis Error: {str(e)}"
                )

# ==========================================
# 9. DISPLAY ANALYSIS RESULTS
# ==========================================

if "analysis" in st.session_state:

    st.divider()

    st.subheader("📊 Medical Image Analysis Results")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Analysis Time",
            f"{st.session_state['elapsed']} sec"
        )

    with col2:

        st.metric(
            "Image Width",
            f"{st.session_state['image_dimensions'][0]} px"
        )

    with col3:

        st.metric(
            "Image Height",
            f"{st.session_state['image_dimensions'][1]} px"
        )

    st.markdown(
        '<div class="result-box">',
        unsafe_allow_html=True
    )

    st.markdown(
        st.session_state["analysis"]
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # ======================================
    # 10. GENERATE DOWNLOADABLE REPORT
    # ======================================

    report = f"""
========================================
             MEDISCAN AI REPORT
========================================

File Name:
{st.session_state['filename']}

Generated Date:
{st.session_state['date']}

Analysis Time:
{st.session_state['elapsed']} seconds

----------------------------------------

AI IMAGE OBSERVATIONS

{st.session_state['analysis']}

----------------------------------------

DISCLAIMER:

This report is generated using Generative AI
for educational demonstration purposes only.

It is NOT a medical diagnosis.

AI-generated observations may be inaccurate
or incomplete.

Consult a qualified radiologist or healthcare
professional for medical interpretation.

========================================
"""

    st.download_button(

        label="⬇ Download Medical Report",

        data=report,

        file_name="MediScan_AI_Report.txt",

        mime="text/plain",

        use_container_width=True
    )

# ==========================================
# 11. FOOTER
# ==========================================

st.divider()

st.caption(
    "MediScan AI | Generative AI Medical Image Analysis"
)

st.caption(
    "Educational prototype only. "
    "Not intended for clinical diagnosis."
)
