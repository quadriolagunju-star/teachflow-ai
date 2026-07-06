from google import genai
import json
import streamlit as st
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

def generate_lesson_and_quiz(topic, level, num_questions=5):
    prompt = f"""
    You are an expert teacher creating a complete, classroom-ready lesson plan.

    Topic: {topic}
    Student level: {level}

    Return ONLY valid JSON (no markdown, no backticks) in this exact structure:
    {{
      "lesson_plan": {{
        "objectives": ["...", "..."],
        "key_concepts": ["...", "..."],
        "timings": [
          {{"segment": "Introduction", "minutes": 5, "activity": "..."}},
          {{"segment": "Direct instruction", "minutes": 15, "activity": "..."}},
          {{"segment": "Guided practice", "minutes": 15, "activity": "..."}},
          {{"segment": "Independent activity", "minutes": 10, "activity": "..."}},
          {{"segment": "Wrap-up", "minutes": 5, "activity": "..."}}
        ],
        "discussion_questions": ["...", "..."],
        "assessment_ideas": ["...", "..."],
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

    text = response.text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None