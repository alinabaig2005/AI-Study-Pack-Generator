import os
import json
import re
from typing import Any, Dict

import streamlit as st
from groq import Groq


st.set_page_config(
    page_title="AI Study Pack Generator",
    page_icon="📚",
    layout="wide",
)


def extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON even if the model wraps it in markdown fences."""
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise ValueError("The AI returned an invalid format. Please try again.")


def generate_study_pack(
    subject: str,
    topic: str,
    level: str,
    exam_type: str,
    language: str,
    number_of_questions: int,
    include_flashcards: bool,
    include_mcqs: bool,
    include_short_questions: bool,
    include_long_questions: bool,
    include_summary: bool,
) -> Dict[str, Any]:

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your environment variables/secrets."
        )

    client = Groq(api_key=api_key)

    selected_sections = []
    if include_summary:
        selected_sections.append("summary")
    if include_flashcards:
        selected_sections.append("flashcards")
    if include_mcqs:
        selected_sections.append("mcqs")
    if include_short_questions:
        selected_sections.append("short_questions")
    if include_long_questions:
        selected_sections.append("long_questions")

    if not selected_sections:
        raise ValueError("Select at least one study-pack section.")

    schema = {
        "title": "string",
        "quick_summary": "string",
        "key_points": ["string"],
        "flashcards": [{"question": "string", "answer": "string"}],
        "mcqs": [
            {
                "question": "string",
                "options": ["string", "string", "string", "string"],
                "correct_answer": "string",
                "explanation": "string",
            }
        ],
        "short_questions": [{"question": "string", "answer": "string"}],
        "long_questions": [{"question": "string", "answer": "string"}],
        "study_tips": ["string"],
    }

    prompt = f"""
You are an expert educational content generator.

Create a high-quality AI study pack.

SUBJECT: {subject}
TOPIC: {topic}
STUDENT LEVEL: {level}
EXAM TYPE: {exam_type}
LANGUAGE: {language}
NUMBER OF QUESTIONS REQUESTED: {number_of_questions}
SECTIONS TO INCLUDE: {", ".join(selected_sections)}

Rules:
1. Teach accurately and at the student's level.
2. Keep explanations clear and exam-focused.
3. Do not invent facts. If a topic is ambiguous, make the most reasonable
   interpretation and state it briefly in the summary.
4. MCQ options must have exactly one correct answer.
5. Short and long answers should be useful for revision and exams.
6. If a section is not requested, return an empty list/string for it.
7. Return ONLY valid JSON. No markdown and no text before or after the JSON.

Return exactly this JSON structure:
{json.dumps(schema, indent=2)}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": "You create accurate, structured study material and always return valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=8000,
    )

    return extract_json(response.choices[0].message.content)


def make_download_text(pack: Dict[str, Any]) -> str:
    lines = [
        f"AI STUDY PACK: {pack.get('title', 'Study Pack')}",
        "=" * 60,
        "",
        "QUICK SUMMARY",
        "-" * 60,
        pack.get("quick_summary", ""),
        "",
        "KEY POINTS",
        "-" * 60,
    ]

    for i, point in enumerate(pack.get("key_points", []), 1):
        lines.append(f"{i}. {point}")

    lines += ["", "FLASHCARDS", "-" * 60]
    for i, card in enumerate(pack.get("flashcards", []), 1):
        lines += [
            f"{i}. Q: {card.get('question', '')}",
            f"   A: {card.get('answer', '')}",
            "",
        ]

    lines += ["MCQs", "-" * 60]
    for i, mcq in enumerate(pack.get("mcqs", []), 1):
        lines.append(f"{i}. {mcq.get('question', '')}")
        for j, option in enumerate(mcq.get("options", []), 1):
            lines.append(f"   {chr(64+j)}. {option}")
        lines.append(f"   Correct: {mcq.get('correct_answer', '')}")
        lines.append(f"   Explanation: {mcq.get('explanation', '')}")
        lines.append("")

    lines += ["SHORT QUESTIONS", "-" * 60]
    for i, item in enumerate(pack.get("short_questions", []), 1):
        lines += [
            f"{i}. Q: {item.get('question', '')}",
            f"   A: {item.get('answer', '')}",
            "",
        ]

    lines += ["LONG QUESTIONS", "-" * 60]
    for i, item in enumerate(pack.get("long_questions", []), 1):
        lines += [
            f"{i}. Q: {item.get('question', '')}",
            f"   A: {item.get('answer', '')}",
            "",
        ]

    lines += ["STUDY TIPS", "-" * 60]
    for i, tip in enumerate(pack.get("study_tips", []), 1):
        lines.append(f"{i}. {tip}")

    return "\n".join(lines)


st.title("📚 AI Study Pack Generator")
st.caption("Generate personalized summaries, flashcards, MCQs, and exam questions with AI.")

with st.sidebar:
    st.header("⚙️ Study Settings")

    subject = st.text_input("Subject", placeholder="e.g. Digital Logic Design")
    topic = st.text_input("Topic", placeholder="e.g. Boolean Algebra")

    level = st.selectbox(
        "Student level",
        ["Beginner", "Intermediate", "Advanced"],
    )

    exam_type = st.selectbox(
        "Exam type",
        ["General Revision", "Quiz", "Midterm", "Final Exam", "Assignment"],
    )

    language = st.selectbox(
        "Language",
        ["English", "Roman Urdu", "Urdu"],
    )

    number_of_questions = st.slider(
        "Number of questions",
        min_value=3,
        max_value=20,
        value=10,
    )

    st.subheader("Include")
    include_summary = st.checkbox("Quick Summary", value=True)
    include_flashcards = st.checkbox("Flashcards", value=True)
    include_mcqs = st.checkbox("MCQs", value=True)
    include_short_questions = st.checkbox("Short Questions", value=True)
    include_long_questions = st.checkbox("Long Questions", value=True)

    generate = st.button("🚀 Generate Study Pack", type="primary", use_container_width=True)


if generate:
    if not subject.strip() or not topic.strip():
        st.error("Please enter both a subject and a topic.")
    else:
        with st.spinner("Generating your study pack..."):
            try:
                st.session_state["study_pack"] = generate_study_pack(
                    subject=subject.strip(),
                    topic=topic.strip(),
                    level=level,
                    exam_type=exam_type,
                    language=language,
                    number_of_questions=number_of_questions,
                    include_flashcards=include_flashcards,
                    include_mcqs=include_mcqs,
                    include_short_questions=include_short_questions,
                    include_long_questions=include_long_questions,
                    include_summary=include_summary,
                )
                st.success("Study pack generated successfully!")
            except Exception as e:
                st.error(str(e))


pack = st.session_state.get("study_pack")

if pack:
    st.header(pack.get("title", "Your Study Pack"))

    if pack.get("quick_summary"):
        st.subheader("📝 Quick Summary")
        st.write(pack["quick_summary"])

    if pack.get("key_points"):
        st.subheader("⭐ Key Points")
        for point in pack["key_points"]:
            st.markdown(f"- {point}")

    if pack.get("flashcards"):
        st.subheader("🧠 Flashcards")
        for i, card in enumerate(pack["flashcards"], 1):
            with st.expander(f"Flashcard {i}: {card.get('question', '')}"):
                st.write(card.get("answer", ""))

    if pack.get("mcqs"):
        st.subheader("❓ MCQs")
        for i, mcq in enumerate(pack["mcqs"], 1):
            st.markdown(f"**{i}. {mcq.get('question', '')}**")
            st.write("")
            options = mcq.get("options", [])
            for option in options:
                st.write(f"- {option}")
            with st.expander("Show answer"):
                st.write(f"**Correct:** {mcq.get('correct_answer', '')}")
                st.write(mcq.get("explanation", ""))

    if pack.get("short_questions"):
        st.subheader("✍️ Short Questions")
        for i, item in enumerate(pack["short_questions"], 1):
            with st.expander(f"{i}. {item.get('question', '')}"):
                st.write(item.get("answer", ""))

    if pack.get("long_questions"):
        st.subheader("📖 Long Questions")
        for i, item in enumerate(pack["long_questions"], 1):
            with st.expander(f"{i}. {item.get('question', '')}"):
                st.write(item.get("answer", ""))

    if pack.get("study_tips"):
        st.subheader("💡 Study Tips")
        for tip in pack["study_tips"]:
            st.markdown(f"- {tip}")

    st.divider()
    st.download_button(
        "⬇️ Download Study Pack (.txt)",
        data=make_download_text(pack),
        file_name="ai_study_pack.txt",
        mime="text/plain",
        use_container_width=True,
    )
else:
    st.info("Enter your subject and topic in the sidebar, choose your sections, and click Generate Study Pack.")
