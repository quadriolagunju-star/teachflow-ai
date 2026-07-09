from fpdf import FPDF
import textwrap
import re


def clean_text(text):
    if not text:
        return ""
    # Normalize all whitespace-like characters (including non-breaking spaces) to a normal space
    text = re.sub(r'[\u00a0\u2000-\u200f\u2028-\u202f]', ' ', text)
    replacements = {
        "'": "'", "'": "'", """: '"', """: '"',
        "–": "-", "—": "-", "…": "...",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    return " ".join(text.split())  # collapse repeated/odd whitespace


def safe_multicell(pdf, text, height=8, width_chars=90):
    """
    Wraps text manually before handing it to FPDF, so a single unbreakable
    'word' (e.g. from a stray non-breaking space) never breaks rendering.
    """
    text = clean_text(text)
    if not text:
        return
    wrapped = textwrap.wrap(text, width=width_chars, break_long_words=True, break_on_hyphens=True)
    for line in wrapped:
        pdf.multi_cell(0, height, line)


def generate_lesson_pdf(lesson_data, subject, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    safe_multicell(pdf, f"{subject}: {topic}", height=10, width_chars=60)
    pdf.ln(5)

    lp = lesson_data["lesson_plan"]

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Objectives", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for obj in lp["objectives"]:
        safe_multicell(pdf, f"- {obj}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Key Concepts", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for kc in lp["key_concepts"]:
        safe_multicell(pdf, f"- {kc}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Explanation", ln=True)
    pdf.set_font("Helvetica", "", 11)
    safe_multicell(pdf, lp.get("explanation", ""))
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Real-World Example", ln=True)
    pdf.set_font("Helvetica", "", 11)
    safe_multicell(pdf, lp.get("real_world_example", ""))
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Quiz", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for i, q in enumerate(lesson_data.get("quiz", []), 1):
        safe_multicell(pdf, f"Q{i}: {q['question']}")
        for opt in q.get("options", []):
            safe_multicell(pdf, f"   {opt}")
        safe_multicell(pdf, f"   Correct answer: {q['correct_answer']}")
        pdf.ln(2)

    return pdf.output(dest="S")