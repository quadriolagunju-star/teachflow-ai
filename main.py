import streamlit as st
from lesson_generator import generate_lesson_and_quiz
from grading_func import smart_grade_and_decide
from onboarding import onboard_teacher
from db import log_feedback 
from pdf_export import generate_lesson_pdf

st.set_page_config(page_title="TeachFlow AI", layout="wide")
st.title("TeachFlow AI")
st.caption("Lesson plans, quizzes, and instant grading — powered by Gemini")

tab0, tab1, tab2 = st.tabs(["👋 Get Started", "📘 Lesson Planner", "📝 Grade a Script"])

# ---------------- TAB 1: LESSON PLANNER ----------------
with tab0:
    st.subheader("Welcome to TeachFlow AI")
    st.caption("Register once — the agent sets up your first lesson automatically.")

    name = st.text_input("Your name")
    email = st.text_input("Email")
    subject = st.text_input("Subject you teach", value="Physics")
    onboard_level = st.selectbox("Level", ["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"], key="onboard_level")
    curriculum = st.selectbox("Curriculum", ["COMMON-ENTRANCE","BECE","GCE","WAEC", "JAMB", "NECO", "POST-UTME"])

    if st.button("Register", type="primary"):
        if not (name and email):
            st.warning("Please enter your name and email.")
        else:
            with st.spinner("Setting up your account and first lesson..."):
                teacher_id, starter_content = onboard_teacher(name, email, subject, onboard_level, curriculum)

            if teacher_id:
                st.session_state["teacher_id"] = teacher_id
                st.session_state["teacher_name"] = name
                st.success(f"Welcome, {name}! Your account is ready.")

                if starter_content:
                    st.markdown("### Here's your first lesson plan, generated automatically:")
                    lp = starter_content["lesson_plan"]
                    st.markdown("**Objectives:**")
                    for obj in lp["objectives"]:
                        st.write("- " + obj)
            else:
                st.error("Something went wrong during registration. Try again.")
with tab1:
    st.subheader("Generate a lesson plan and quiz")
    subject = st.text_input("Subject", placeholder = "e.g. Physics")
    topic = st.text_input("Topic", placeholder="e.g. Newton's Second Law of Motion")
    grade_level = st.selectbox("Student level", ["NURSERY1","NURSERY2","BASIC1","BASIC2","BASIC3","BASIC4","BASIC5","BASIC6","JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"], index=5)
    num_questions = st.slider("Number of quiz questions", 3, 10, 5)
    g_teacher_id = st.session_state.get("teacher_id", "demo_teacher")
    if st.button("Generate Lesson Plan", type="primary"):
        if not topic:
            st.warning("Enter a topic first.")
        else:
            with st.spinner("Generating..."):
                full_topic = f"{subject}:{topic}"
                result = generate_lesson_and_quiz(full_topic, grade_level, num_questions)

            if result:
                lp = result["lesson_plan"]
                st.markdown("### Objectives")
                for obj in lp["objectives"]:
                    st.write("- " + obj)
                st.markdown("---")
                st.write("Was this helpful?")
                rating = st.feedback("thumbs", key="lesson_feedback_rating")
                comment = st.text_input("Any comments? (optional)")
                if rating is not None:
                    log_feedback(g_teacher_id, "lesson_plan", rating, comment)
                    st.success("Thanks for your feedback!")

                st.markdown("### Key Concepts")
                for kc in lp["key_concepts"]:
                    st.write("- " + kc)

                st.markdown("### Explanation")
                st.write(lp["explanation"])

                st.markdown("### Real-World Example")
                st.write(lp["real_world_example"])

                st.markdown("### Quiz")
                for i, q in enumerate(result["quiz"], 1):
                    st.write(f"**Q{i}: {q['question']}**")
                    for opt in q["options"]:
                        st.write(opt)
                    with st.expander("Show answer"):
                        st.write(f"Correct answer: {q['correct_answer']}")
                        st.write(q["explanation"])
                st.markdown("---")
                st.subheader("Export this lesson")
                col1, col2, col3 = st.columns(3)
                
            with col1:
                with col1:
                        pdf_bytes = generate_lesson_pdf(result, subject, topic)
                        st.download_button(
                            "📄 Export as PDF",
                            data=pdf_bytes,
                            file_name=f"{topic.replace(' ', '_')}_lesson_plan.pdf",
                            mime="application/pdf"
                        )
            with col2:
                if st.button("📊 Export as Slides"):
                    st.session_state["export_requested"] = "slides"
            with col3:
                if st.button("☁️ Save to Google Drive"):
                    st.session_state["export_requested"] = "drive"
    
            if st.session_state.get("export_requested"):
                st.info("✨ Exports are a **Pro** feature. Upgrade to unlock PDF, Slides, and Google Drive export.")
                if st.button("Upgrade to Pro"):
                    st.session_state["show_upgrade"] = True
    
            if st.session_state.get("show_upgrade"):
                st.markdown("""
                ### TeachFlow Pro — ₦2,500/month
                - Unlimited PDF & Slides export
                - Google Drive sync
                - Priority grading speed
                """)
                st.button("Continue to Payment (coming soon)")
            else:
                st.error("Something went wrong generating the lesson. Try again.")

# ---------------- TAB 2: GRADE A SCRIPT ----------------
with tab2:
    st.subheader("Snap or upload a student's answer sheet")

    


    st.caption("Fill in the fields below for strict rubric grading, or leave them blank and let the agent detect everything.")
    
    g_student_name = st.text_input("Student name")
    g_teacher_id = st.session_state.get("teacher_id", "demo_teacher")
    g_topic = st.text_input("Topic (optional)", placeholder="e.g. Newton's Second Law of Motion")
    g_question = st.text_area("Question (optional)", placeholder="Paste the exact question here")
    g_correct_answer = st.text_area("Expected/model answer (optional)")
    g_total_marks = st.number_input("Total marks", min_value=1, max_value=100, value=10)
    
    uploaded_image = st.camera_input("Take a photo of the answer sheet") or \
                      st.file_uploader("...or upload an image", type=["jpg", "jpeg", "png"])
    
    if st.button("Grade Answer", type="primary"):
        if not (g_student_name and uploaded_image):
            st.warning("Enter student name and provide an image.")
        else:
            with open("temp_upload.jpg", "wb") as f:
                f.write(uploaded_image.getbuffer())
    
            with st.spinner("Reading script and grading..."):
                result, action = smart_grade_and_decide(
                    image_path="temp_upload.jpg",
                    student_id=g_student_name,
                    teacher_id=g_teacher_id,
                    topic=g_topic or None,
                    question=g_question or None,
                    correct_answer=g_correct_answer or None,
                    total_marks=g_total_marks
                )
    
            if result:
                st.markdown(f"### Detected Topic: {result['detected_topic']}")
                st.markdown(f"### Question: {result['detected_question']}")
                st.markdown("### Extracted Answer")
                st.info(result["extracted_answer"])
                st.markdown(f"### Score: {result['score']} / {g_total_marks}")
                st.write(f"**Verdict:** {result['verdict']}")
    
                st.markdown("### Feedback")
                st.write(result["feedback"])
    
                st.markdown("### Missing Concepts")
                for mc in result["missing_concepts"]:
                    st.write("- " + mc)
    
                st.markdown("### Improvement Tip")
                st.write(result["improvement_tip"])
                st.markdown("---")
                
                st.write("Was this helpful?")
                rating = st.feedback("thumbs",key = "grading_feedback_rating")  # Streamlit's built-in thumbs up/down widget
                comment = st.text_input("Any comments? (optional)")
                if rating is not None:
                    log_feedback(g_teacher_id, "grading", rating, comment)
                    st.success("Thanks for your feedback!")
                    st.markdown("---")
                    
                if action == "escalate":
                    st.error("⚠️ Low score — flagged for your review.")
                elif action == "auto_remediate":
                    st.warning("📘 Score suggests extra practice — remedial worksheet queued.")
                else:
                    st.success("✅ Strong performance — no action needed.")
            else:
                st.error("Could not grade this image. Try a clearer photo.")
                
    from retention import run_retention_check
    
    with st.sidebar:
        st.subheader("🔁 Retention Agent (Admin)")
        if st.button("Run retention check now"):
            with st.spinner("Checking inactive teachers..."):
                results = run_retention_check()
            if results:
                for r in results:
                    st.write(f"**{r['teacher']}** → {r['action']}: {r['message']}")
            else:
                st.info("No inactive teachers found.")