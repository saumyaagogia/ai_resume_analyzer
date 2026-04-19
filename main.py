
import streamlit as st
from openai import OpenAI
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
import re
import pandas as pd
import json

# Load API key
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page config
st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("📄 AI Resume Analyzer")
st.markdown("Upload your resume and get a **summary, key skills, score, and improvement suggestions**")

# File upload
uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])

# Function to extract text
def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

if uploaded_file:
    text = extract_text(uploaded_file)

    # Clean text
    text_clean = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Layout
    col1, col2 = st.columns([1, 1])

    # LEFT SIDE
    with col1:
        st.subheader("📄 Resume Preview")
        st.text_area("Resume Text", value=text_clean, height=400)

    # RIGHT SIDE
    with col2:
        st.subheader("🤖 AI Analysis")

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing resume..."):

                prompt = f"""
You are a professional resume expert.

Analyze the following resume and provide:
1. A short Summary
2. Key Skills (bullet points)
3. Suggestions for improvement

4. Give a score out of 100 based on:
   - Skills match (30 points)
   - Experience & achievements (30 points)
   - Clarity & formatting (20 points)
   - Overall impression (20 points)

At the end, strictly output ONLY this JSON format:

Score JSON:
{{
  "Skills": number,
  "Experience": number,
  "Clarity": number,
  "Overall": number
}}

Resume:
{text_clean}
"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )

                result = response.choices[0].message.content

                # Split text and JSON
                parts = result.split("Score JSON:")
                analysis_text = parts[0]

                st.write(analysis_text)

                # Parse JSON
                if len(parts) > 1:
                    try:
                        score_data = json.loads(parts[1].strip())

                        st.subheader("📊 Score Breakdown")

                        df = pd.DataFrame({
                            "Category": list(score_data.keys()),
                            "Score": list(score_data.values())
                        })

                        st.bar_chart(df.set_index("Category"))

                        st.subheader("🏁 Overall Score")
                        total_score = sum(score_data.values())

                        st.progress(total_score / 100)
                        st.write(f"**Total Score: {total_score}/100**")

                    except Exception as e:
                        st.warning("Could not parse score JSON")
                        st.text(str(e))