from utils import llm


def get_ai_feedback(resume_text: str, extracted_skills: list, target_role: str = "", experience_level: str = "Auto-Detect") -> dict:
    """
    Uses Groq/LLM to analyze the resume and return structured feedback.
    Strictly enforces experience-level-appropriate role suggestions.
    """

    if experience_level != "Auto-Detect":
        exp_context = f"""The candidate's experience level is: {experience_level}.
CRITICAL: You MUST only suggest roles that are appropriate for this exact level.
- Internship: suggest only internship positions
- Entry Level / Junior: suggest only junior/entry-level roles (0-2 years experience required)
- Mid-Level: suggest roles requiring 2-5 years
- Senior / Lead: suggest senior/lead roles
Do NOT suggest roles above their level under any circumstances."""
    else:
        exp_context = """Carefully analyze the resume to PREDICT the candidate's experience level.
Look for: years of experience, job titles held, number of projects, education status (student vs graduate).
If they appear to be a student or recent graduate with no work experience, classify as Internship or Entry Level.
CRITICAL: Only suggest roles matching the level you predict."""

    if target_role:
        role_context = f"The candidate is targeting: {target_role}. Provide feedback focused on this role, but at their experience level (add 'Junior', 'Entry-Level', etc. prefix as needed)."
        json_instruction = f"""Return a JSON object with three keys:
1. "suggested_roles": A list of 2 role strings — the target role adjusted for their level (e.g. "Junior {target_role}", "Entry-Level {target_role}").
2. "predicted_level": The evaluated experience level string (e.g. "Entry Level").
3. "feedback": A markdown string with: strengths, missing skills for the role, and 2-3 actionable resume improvements."""
    else:
        json_instruction = """Return a JSON object with three keys:
1. "suggested_roles": A list of 3 HIGHLY SPECIFIC, level-appropriate job titles. Bad example: "Software Engineer". Good examples: "Junior Python Developer", "Data Analyst Intern", "Entry-Level Machine Learning Engineer".
2. "predicted_level": The evaluated experience level string (e.g. "Entry Level").
3. "feedback": A markdown string with: overall strengths, top missing skills for the suggested roles, and 2-3 actionable resume improvements."""
        role_context = "Infer the best fitting roles based on their exact skills AND experience level."

    prompt = f"""You are an expert technical recruiter specializing in matching candidates to level-appropriate jobs.

RESUME TEXT:
---
{resume_text[:3000]}
---

EXTRACTED SKILLS: {', '.join(extracted_skills)}

EXPERIENCE LEVEL RULES:
{exp_context}

TASK: {role_context}

{json_instruction}

Return ONLY valid JSON. No extra commentary."""

    try:
        return llm.ask_json(prompt)
    except Exception as e:
        default_role = target_role if target_role else "Software Engineer"
        return {
            "suggested_roles": [default_role],
            "predicted_level": experience_level,
            "feedback": f"AI feedback generation failed.\n\n**Error:** `{e}`\n\nCheck your `GROQ_API_KEY` in the `.env` file.",
        }
