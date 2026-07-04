from fpdf import FPDF


def generate_lesson_pdf(lesson_data, subject, topic):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, f"{subject}: {topic}", align="C")
    pdf.ln(5)

    lp = lesson_data["lesson_plan"]

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Objectives", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for obj in lp["objectives"]:
        pdf.multi_cell(0, 8, f"- {obj}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Key Concepts", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for kc in lp["key_concepts"]:
        pdf.multi_cell(0, 8, f"- {kc}")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Explanation", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, lp["explanation"])
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Real-World Example", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 8, lp["real_world_example"])
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Quiz", ln=True)
    pdf.set_font("Helvetica", "", 11)
    for i, q in enumerate(lesson_data["quiz"], 1):
        pdf.multi_cell(0, 8, f"Q{i}: {q['question']}")
        for opt in q["options"]:
            pdf.multi_cell(0, 7, f"   {opt}")
        pdf.multi_cell(0, 7, f"   Correct answer: {q['correct_answer']}")
        pdf.ln(2)

    return pdf.output(dest="S")