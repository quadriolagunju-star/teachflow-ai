import streamlit as st
from lesson_generator import generate_lesson_and_quiz
from grading_func import grade_answer_sheet_from_image

st.set_page_config(page_title="TeachFlow AI", layout="wide")
st.title("TeachFlow AI")
st.caption("Lesson plans, quizzes, and instant grading — powered by Gemini")

tab1, tab2 = st.tabs(["📘 Lesson Planner", "📝 Grade a Script"])

# ---------------- TAB 1: LESSON PLANNER ----------------
with tab1:
    st.subheader("Generate a lesson plan and quiz")
    topic = st.text_input("Topic", placeholder="e.g. Newton's Second Law of Motion")
    grade_level = st.selectbox("Student level", ["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"], index=5)
    num_questions = st.slider("Number of quiz questions", 3, 10, 5)

    if st.button("Generate Lesson Plan", type="primary"):
        if not topic:
            st.warning("Enter a topic first.")
        else:
            with st.spinner("Generating..."):
                result = generate_lesson_and_quiz(topic, grade_level, num_questions)

            if result:
                lp = result["lesson_plan"]
                st.markdown("### Objectives")
                for obj in lp["objectives"]:
                    st.write("- " + obj)

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
            else:
                st.error("Something went wrong generating the lesson. Try again.")

# ---------------- TAB 2: GRADE A SCRIPT ----------------
with tab2:
    st.subheader("Snap or upload a student's answer sheet")

    g_topic = st.text_input("Topic ", placeholder="e.g. Newton's Second Law of Motion", key="grade_topic")
    g_question = st.text_area("Question", placeholder="Paste the exact question here")
    g_correct_answer = st.text_area("Expected/model answer")
    g_total_marks = st.number_input("Total marks", min_value=1, max_value=100, value=10)

    uploaded_image = st.camera_input("Take a photo of the answer sheet") or \
                      st.file_uploader("...or upload an image", type=["jpg", "jpeg", "png"])

    if st.button("Grade Answer", type="primary"):
        if not (g_topic and g_question and g_correct_answer and uploaded_image):
            st.warning("Fill in all fields and provide an image.")
        else:
            with open("temp_upload.jpg", "wb") as f:
                f.write(uploaded_image.getbuffer())

            with st.spinner("Reading and grading..."):
                result = grade_answer_sheet_from_image(
                    image_path="temp_upload.jpg",
                    question=g_question,
                    correct_answer=g_correct_answer,
                    topic=g_topic,
                    total_marks=g_total_marks
                )

            if result:
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
            else:
                st.error("Could not grade this image. Try a clearer photo.")