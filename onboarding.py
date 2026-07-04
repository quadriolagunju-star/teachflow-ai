from db import register_teacher, log_event
from lesson_generator import generate_lesson_and_quiz

def onboard_teacher(name, email, subject, level, curriculum):
    teacher_id = register_teacher(name, email, subject, level, curriculum)
    if not teacher_id:
        return None, None

    starter_content = generate_lesson_and_quiz(subject, level, 5)

    log_event(teacher_id, "onboarding_complete", {
        "name": name,
        "email": email,
        "subject": subject,
        "level": level,
        "curriculum": curriculum
    })

    return teacher_id, starter_content