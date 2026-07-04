from google import genai
from google.genai import types
import json
import streamlit as st
from db import get_inactive_teachers, log_event
from lesson_generator import generate_lesson_and_quiz

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])


def decide_retention_action(teacher):
    prompt = f"""
    A teacher named {teacher['name']} who teaches {teacher['subject']} at {teacher['level']} level
    has not used TeachFlow AI in over 5 days.

    Decide: should we send them a ready-made lesson to re-engage them,
    or a simple check-in nudge?

    Return ONLY valid JSON (no markdown, no backticks) in this structure:
    {{"action": "send_lesson" or "nudge", "message": "A short, warm message to the teacher explaining why we're reaching out."}}
    """
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt]
    )
    text = response.text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"action": "nudge", "message": "We miss you! Come back and try TeachFlow AI."}


def run_retention_check():
    """
    Checks all inactive teachers, decides what to do for each,
    and logs the action. Returns a summary list for display/testing.
    """
    inactive = get_inactive_teachers(days=5)
    results = []

    for teacher in inactive:
        decision = decide_retention_action(teacher)

        if decision["action"] == "send_lesson":
            content = generate_lesson_and_quiz(teacher["subject"], teacher["level"], 3)
        else:
            content = None

        log_event(teacher["id"], "retention_action", {
            "action": decision["action"],
            "message": decision["message"]
        })

        results.append({
            "teacher": teacher["name"],
            "action": decision["action"],
            "message": decision["message"]
        })

    return results