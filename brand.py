import streamlit as st
from openai import OpenAI
from docx import Document

# --- PAGE SETUP ---
st.set_page_config(page_title="Template-Based Story Generator", layout="wide")
st.title("📄 Template-Based Business Profile Generator")

# --- INPUTS ---
owner_name = st.text_input("Name")
title = st.text_input("Title")
company_name = st.text_input("Company Name")
ccib_since = st.text_input("With CCIB since")

template_file = st.file_uploader("Upload Template (.docx)", type=["docx"])
uploaded_file = st.file_uploader("Upload Interview (.docx)", type=["docx"])

# --- LOAD API KEY FROM SECRETS ---
if "OPENAI_API_KEY" not in st.secrets:
    st.error("Missing API key in Streamlit secrets.")
    st.stop()

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# --- FUNCTIONS ---
def extract_text(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])


def extract_key_points(text):
    lines = text.split("\n")
    important = []

    keywords = [
        "founded", "started", "experience", "success", "rate",
        "challenge", "problem", "solution", "growth",
        "partner", "relationship", "worked with",
        "certification", "inspiration", "client"
    ]

    for line in lines:
        for word in keywords:
            if word.lower() in line.lower():
                important.append(line.strip())
                break

    return list(set(important))[:20]


def generate_story(name, title, company, ccib, transcript, template_text):
    prompt = f"""
You are a professional business writer AND analyst.

GOAL:
Recreate the business profile using the SAME structure, tone, and style as the template.

CRITICAL INSTRUCTIONS:
- Follow template EXACTLY
- Do NOT skip sections if info exists
- Extract aggressively from transcript
- Reword professionally
- NEVER invent details
- If truly missing → write: ⚠️ Information not provided

SPECIAL FOCUS:
- Look carefully for partnerships, collaborations, or organizations mentioned
- Expand slightly on relationships if present
- Ensure NOTHING obvious is missed

TEMPLATE:
{template_text}

INPUT:
{transcript}

BUSINESS INFO:
Name: {name}
Title: {title}
Company: {company}
With CCIB since: {ccib}
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"Error: {str(e)}"


# --- VALIDATION ---
if not template_file or not uploaded_file:
    st.warning("Please upload both a template and an interview file.")

# --- MAIN ACTION ---
if template_file and uploaded_file and owner_name and company_name:

    if st.button("Generate Story"):
        with st.spinner("Generating..."):

            template_text = extract_text(template_file)
            transcript = extract_text(uploaded_file)

            output = generate_story(
                owner_name,
                title,
                company_name,
                ccib_since,
                transcript,
                template_text
            )

            highlights = extract_key_points(transcript)

        st.subheader("Generated Story")
        st.text_area("", output, height=500)

        st.subheader("🔍 Extracted Source Highlights (for verification)")
        for h in highlights:
            st.markdown(f"- {h}")

        st.text_area("Source Highlights (copyable)", "\n".join(highlights), height=200)