from google import genai
from google.genai import types
import json
import streamlit as st
from db import log_event
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def smart_grade_from_image(image_path, topic=None, question=None, correct_answer=None, total_marks=10):
    """
    Grades a student's answer sheet. If topic/question/correct_answer are provided,
    grades strictly against them. If left blank, the agent detects them itself.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    if topic and question and correct_answer:
        # Manual mode — strict rubric grading
        context_block = f"""
        Topic: {topic}
        Question: {question}
        Expected/model answer: {correct_answer}
        Grade strictly against this expected answer.
        """
    else:
        # Auto mode — agent detects everything itself
        context_block = """
        No topic, question, or expected answer was provided.
        Identify the topic and question from the image yourself,
        determine the correct answer using standard physics principles,
        then grade against your own determination.
        """

    prompt = f"""
    You are a strict but fair physics teacher grading a student's handwritten or typed answer sheet.

    {context_block}

    Total marks available: {total_marks}

    Look at the image. Read the student's handwriting/text carefully, even if messy.

    Return ONLY valid JSON (no markdown, no backticks) in this exact structure:
    {{
      "detected_topic": "...",
      "detected_question": "...",
      "correct_answer": "...",
      "extracted_answer": "What you read from the student's handwriting, transcribed as text.",
      "score": <integer from 0 to {total_marks}>,
      "verdict": "...",
      "feedback": "...",
      "missing_concepts": ["..."],
      "improvement_tip": "..."
    }}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt
        ]
    )

    text = response.text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

# --- Test it directly when this file is run on its own ---
if __name__ == "__main__":
    result = result = smart_grade_from_image(image_path="sample_answer_sheet.jpg", total_marks=10)

    if result:
        print("Extracted answer:", result["extracted_answer"])
        print("Score:", result["score"], "/10")
        print("Verdict:", result["verdict"])
        print("Feedback:", result["feedback"])
        print("Missing concepts:", result["missing_concepts"])
        print("Tip:", result["improvement_tip"])
        
        
def smart_grade_and_decide(image_path, student_id, teacher_id, topic=None, question=None, correct_answer=None, total_marks=10):
    result = smart_grade_from_image(image_path, topic, question, correct_answer, total_marks)
    if not result:
        return None, None

    score_pct = (result["score"] / total_marks) * 100
    if score_pct < 50:
        action = "escalate"
    elif score_pct < 75:
        action = "auto_remediate"
    else:
        action = "none"

    mode = "manual" if (topic and question and correct_answer) else "auto"
    log_event(teacher_id, "grading_decision", {
        "student_id": student_id,
        "topic": result["detected_topic"],
        "score": result["score"],
        "action": action,
        "mode": mode
    })

    return result, action