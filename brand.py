import streamlit as st
from docx import Document
from openai import OpenAI

# --- SETUP ---
st.set_page_config(page_title="Template-Based Story Generator", layout="wide")
st.title("📄 Template-Based Business Profile Generator")

# --- INPUTS ---
owner_name = st.text_input("Owner Name")
company_name = st.text_input("Company Name")

location = st.text_input("Location (optional)")
industry = st.text_input("Industry (optional)")

template_file = st.file_uploader("Upload Template (.docx)", type=["docx"])
uploaded_file = st.file_uploader("Upload Interview (.docx)", type=["docx"])

# --- LOAD API KEY FROM SECRETS ---
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except Exception:
    st.error("Missing API key. Add it to Streamlit secrets.")
    st.stop()

# --- FUNCTIONS ---

def extract_text(file):
    doc = Document(file)
    return "\n".join([p.text.strip() for p in doc.paragraphs if p.text.strip()])


def extract_key_points(text):
    lines = text.split("\n")
    important = []

    keywords = [
        "founded", "started", "experience", "success", "rate",
        "challenge", "problem", "solution", "growth",
        "partner", "partnership", "client", "relationship",
        "certification", "inspiration", "why", "how"
    ]

    for line in lines:
        for word in keywords:
            if word in line.lower():
                important.append(line.strip())
                break

    return list(dict.fromkeys(important))[:25]


def generate_story(owner, company, transcript, template_text, location, industry):
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are a professional business writer AND analyst.

Your job:
Recreate a business profile using the SAME structure, tone, and style as the template.

BUT:
- Pull ALL possible details from the transcript
- Do NOT miss information
- Expand where appropriate
- If partnerships or relationships are mentioned → highlight and expand them clearly

CONTEXT:
Owner: {owner}
Company: {company}
Location: {location}
Industry: {industry}

TEMPLATE:
{template_text}

TRANSCRIPT:
{transcript}

RULES:
- Follow template EXACTLY
- Extract EVERYTHING relevant
- If info exists → USE IT
- Only use ⚠️ if truly missing
- Maintain strong professional tone

GOAL:
Output should feel like the template rewritten using the transcript,
but MORE complete and detailed.
"""

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output[0].content[0].text
    except Exception as e:
        return f"Error: {str(e)}"


# --- MAIN ---
if st.button("Generate Story"):

    if not template_file or not uploaded_file:
        st.warning("Please upload BOTH a template and interview file.")
    else:
        with st.spinner("Generating..."):

            template_text = extract_text(template_file)
            transcript = extract_text(uploaded_file)

            st.subheader("📄 Transcript Preview")
            st.text_area("", transcript[:2000], height=200)

            output = generate_story(
                owner_name,
                company_name,
                transcript,
                template_text,
                location,
                industry
            )

            highlights = extract_key_points(transcript)

        st.subheader("Generated Story")
        st.text_area("", output, height=500)

        st.subheader("🔍 Extracted Source Highlights")
        st.text_area("", "\n".join(highlights), height=200)