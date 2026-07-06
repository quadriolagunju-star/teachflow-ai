from google import genai
import json
import streamlit as st

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def generate_parent_message(student_name, message_type, context):
    """
    message_type: 'behavior', 'achievement', or 'meeting_request'
    """
    prompt = f"""
    You are a teacher writing an email to a parent.

    Student: {student_name}
    Message type: {message_type}
    Context/details: {context}

    Write a warm, professional, concise email (not more than 150 words).

    Return ONLY valid JSON (no markdown, no backticks):
    {{"subject": "...", "body": "..."}}
    """
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = response.text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None