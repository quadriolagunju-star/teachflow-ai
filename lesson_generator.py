from google import genai
import json
import streamlit as st
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def generate_lesson_and_quiz(topic, level, num_questions=5):
    prompt = f"""
You are an expert teacher creating classroom-ready materials.

Topic: {topic}
Student level: {level}

Return ONLY valid JSON (no markdown, no backticks) in this exact structure:

{{
  "lesson_plan": {{
    "objectives": ["...", "..."],
    "key_concepts": ["...", "..."],
    "explanation": "A clear, well-structured explanation of the topic suitable for the student level.",
    "real_world_example": "A relatable example connecting the concept to everyday life."
  }},
  "quiz": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_answer": "A",
      "explanation": "Why this is correct."
    }}
  ]
}}

Generate exactly {num_questions} quiz questions, multiple choice, increasing in difficulty.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw_text = response.text.strip()
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.replace("json", "", 1).strip()
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        print("Could not parse JSON. Raw output:")
        print(raw_text)
        return None