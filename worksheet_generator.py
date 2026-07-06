from google import genai
import json
import streamlit as st

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def generate_worksheet(topic=None, source_text=None, level="SS1", formats=None, num_items=10):
    """
    Generates a worksheet/quiz. Either from a topic, or from uploaded text (source_text).
    formats: list from ["multiple_choice", "short_answer", "fill_in_blank"]
    """
    formats = formats or ["multiple_choice"]

    if source_text:
        context = f"Base all questions strictly on this text:\n\n{source_text}"
    else:
        context = f"Topic: {topic}"

    prompt = f"""
    You are a teacher creating a worksheet for {level} students.

    {context}

    Include these question formats: {', '.join(formats)}.
    Generate {num_items} total questions, mixed across the requested formats.

    Return ONLY valid JSON (no markdown, no backticks) in this structure:
    {{
      "title": "...",
      "questions": [
        {{
          "type": "multiple_choice" or "short_answer" or "fill_in_blank",
          "question": "...",
          "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
          "answer": "..."
        }}
      ]
    }}
    For short_answer and fill_in_blank, "options" can be an empty list.
    """

    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    text = response.text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None