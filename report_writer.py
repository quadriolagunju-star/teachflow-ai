from google import genai
import json
import streamlit as st

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def generate_progress_report(student_name, teacher_notes, tone="professional"):
    prompt = f"""
    You are a teacher writing a student progress report.

    Student: {student_name}
    Teacher's raw notes: {teacher_notes}

    Turn these notes into a polished, {tone} progress report paragraph (3-5 sentences),
    suitable to share with parents. Be specific and constructive, not generic.

    Return ONLY valid JSON (no markdown, no backticks):
    {{"report": "..."}}
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = response.text.strip()
    try:
        return json.loads(text)["report"]
    except (json.JSONDecodeError, KeyError):
        return None