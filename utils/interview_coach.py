from utils import llm


def generate_interview_prep(resume_text: str, target_role: str = "", experience_level: str = "Auto-Detect") -> dict:
    """
    Generates a full interview prep package: behavioral questions,
    technical questions, and a study roadmap.
    """

    prompt = f"""You are an expert interview coach.

Based on the candidate's resume below, generate a complete interview preparation package.

Return ONLY a JSON object with these exact keys:

{{
  "behavioral_questions": [
    {{
      "question": "<behavioral interview question>",
      "why_asked": "<one sentence on what the interviewer is looking for>",
      "answer_hint": "<brief tip on how to answer using their background>"
    }}
  ],
  "technical_questions": [
    {{
      "question": "<technical question specific to the role>",
      "difficulty": "Easy | Medium | Hard",
      "topic": "<topic area e.g. SQL, System Design>"
    }}
  ],
  "study_roadmap": [
    {{
      "topic": "<topic name>",
      "why": "<one sentence why this matters for the role>",
      "free_resource": "<specific free resource e.g. 'freeCodeCamp SQL course on YouTube'>"
    }}
  ],
  "answer_evaluator_ready": true
}}

Provide exactly 4 behavioral_questions, 5 technical_questions, and 4-5 study_roadmap items.

Resume:
{resume_text}

Target Role: {target_role or "Not specified"}
Experience Level: {experience_level}"""

    try:
        return llm.ask_json(prompt)
    except Exception as e:
        return {
            "behavioral_questions": [],
            "technical_questions": [],
            "study_roadmap": [],
            "answer_evaluator_ready": False,
            "error": str(e),
        }


def evaluate_answer(question: str, user_answer: str, resume_text: str) -> dict:
    """
    Evaluates a user's interview answer against the question and their resume.
    """

    prompt = f"""You are an expert interview coach evaluating a candidate's answer.

Question: {question}

Candidate's Answer: {user_answer}

Candidate's Resume (for context):
{resume_text[:1000]}

Return ONLY a JSON object with these exact keys:
{{
  "score": <int 0-10>,
  "feedback": "<2-3 sentences of specific, actionable feedback>",
  "better_answer": "<a stronger version of their answer using details from their resume>"
}}"""

    try:
        return llm.ask_json(prompt)
    except Exception as e:
        return {
            "score": 0,
            "feedback": f"Failed to evaluate answer: {e}",
            "better_answer": "",
        }
