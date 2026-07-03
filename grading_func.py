from google import genai
from google.genai import types
import json
import streanlit as st
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def grade_answer_sheet_from_image(image_path, question, correct_answer, topic, total_marks=10):
    """
    Takes a photo of a student's answer sheet and grades it using Gemini's vision.
    Returns a dict with score, verdict, feedback, missing concepts, and a tip.
    """

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    prompt = f"""
You are a strict but fair physics teacher grading a student's handwritten or typed answer sheet.

Topic: {topic}
Question: {question}
Expected/model answer: {correct_answer}
Total marks available: {total_marks}

Look at the image of the student's answer sheet. Read their handwriting/text carefully,
even if messy, and grade what they wrote.

Return ONLY valid JSON (no markdown, no backticks) in this exact structure:

{{
  "extracted_answer": "What you read from the student's handwriting, transcribed as text.",
  "score": <integer from 0 to {total_marks}>,
  "verdict": "correct" | "partially correct" | "incorrect",
  "feedback": "Specific, encouraging feedback explaining what was right or wrong.",
  "missing_concepts": ["...", "..."],
  "improvement_tip": "One clear, actionable tip to help the student improve."
}}

Be fair: give partial credit for correct reasoning even if the final answer is slightly off
or handwriting makes some words unclear. If truly illegible, note that in feedback.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt
        ]
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


# --- Test it directly when this file is run on its own ---
if __name__ == "__main__":
    result = grade_answer_sheet_from_image(
        image_path="sample_answer_sheet.jpg",
        question="A 5kg object experiences a net force of 20N. What is its acceleration?",
        correct_answer="a = F/m = 20/5 = 4 m/s²",
        topic="Newton's Second Law of Motion",
        total_marks=10
    )

    if result:
        print("Extracted answer:", result["extracted_answer"])
        print("Score:", result["score"], "/10")
        print("Verdict:", result["verdict"])
        print("Feedback:", result["feedback"])
        print("Missing concepts:", result["missing_concepts"])
        print("Tip:", result["improvement_tip"])