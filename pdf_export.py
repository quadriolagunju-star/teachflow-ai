from fpdf import FPDF
import textwrap
import re


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r'[\u00a0\u2000-\u200f\u2028-\u202f]', ' ', text)
    replacements = {
        "'": "'", "'": "'", """: '"', """: '"',
        "–": "-", "—": "-", "…": "...",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    text = text.encode("latin-1", "ignore").decode("latin-1")
    return " ".join(text.split())


def safe_multicell(pdf, text, height=8, width_chars=70):
    """
    Wraps and renders text defensively. If FPDF still can't fit a line
    (character metrics vary), it retries with progressively shorter
    chunks instead of crashing.
    """
    text = clean_text(text)
    if not text:
        return

    wrapped = textwrap.wrap(text, width=width_chars, break_long_words=True, break_on_hyphens=True)
    if not wrapped:
        wrapped = [text]

    for line in wrapped:
        _render_line_safely(pdf, line, height)


def _render_line_safely(pdf, line, height):
    try:
        pdf.multi_cell(0, height, line)
    except Exception:
        # Fallback: split into smaller and smaller chunks until it fits
        chunk_size = max(1, len(line) // 2)
        while chunk_size >= 1:
            try:
                for i in range(0, len(line), chunk_size):
                    pdf.multi_cell(0, height, line[i:i + chunk_size])
                return
            except Exception:
                chunk_size //= 2
        # Absolute last resort: skip this line rather than crash the whole PDF
        pass


def generate_lesson_pdf(lesson_data, subject, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    safe_multicell(pdf, f"{subject}: {topic}", height=10, width_chars=50)
    pdf.ln(5)

    lp = lesson_data["lesson_plan"]

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Objectives", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for obj in lp.get("objectives", []):
        safe_multicell(pdf, f"- {obj}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Key Concepts", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for kc in lp.get("key_concepts", []):
        safe_multicell(pdf, f"- {kc}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Lesson Timing & Activities", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for seg in lp.get("timings", []):
        safe_multicell(pdf, f"{seg.get('segment','')} ({seg.get('minutes','')} min): {seg.get('activity','')}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Discussion Questions", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for dq in lp.get("discussion_questions", []):
        safe_multicell(pdf, f"- {dq}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Assessment Ideas", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for ai in lp.get("assessment_ideas", []):
        safe_multicell(pdf, f"- {ai}")
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
        safe_multicell(pdf, f"Q{i}: {q.get('question','')}")
        for opt in q.get("options", []):
            safe_multicell(pdf, f"   {opt}")
        safe_multicell(pdf, f"   Correct answer: {q.get('correct_answer','')}")
        pdf.ln(2)

    return pdf.output(dest="S")