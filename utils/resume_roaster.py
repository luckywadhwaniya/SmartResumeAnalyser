from utils import llm


def roast_resume(resume_text: str, target_role: str = "", experience_level: str = "Auto-Detect") -> dict:
    """
    Sends the full resume to Gemini for a brutally honest analysis.
    Returns a structured dict with scores, roast, strengths, weak bullets,
    missing sections, clichés, and a tailored cover letter.
    """

    prompt = f"""You are a brutally honest but constructive career coach and resume expert.

Analyze this resume and return ONLY a JSON object with these exact keys:

{{
  "overall_score": <int 0-100>,
  "dimension_scores": {{
    "clarity": <int 0-100>,
    "impact": <int 0-100>,
    "ats_friendliness": <int 0-100>,
    "keyword_density": <int 0-100>
  }},
  "roast": "<2-3 sentence brutally honest summary of the resume's biggest weaknesses>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>"],
  "weak_bullets": [
    {{
      "original": "<exact weak bullet point from resume>",
      "rewritten": "<stronger quantified version>"
    }}
  ],
  "missing_sections": ["<section 1>", "<section 2>"],
  "cliches_found": ["<cliche phrase 1>", "<cliche phrase 2>"],
  "cover_letter": "<a tailored 3-paragraph cover letter for the target role, or a general one if no role specified>"
}}

Provide up to 4 entries in weak_bullets. Be specific — quote actual text from the resume.

Resume:
{resume_text}

Target Role: {target_role or "Not specified"}
Experience Level: {experience_level}"""

    try:
        return llm.ask_json(prompt)
    except Exception as e:
        return {
            "overall_score": 0,
            "dimension_scores": {"clarity": 0, "impact": 0, "ats_friendliness": 0, "keyword_density": 0},
            "roast": f"Failed to analyze resume: {e}",
            "strengths": [],
            "weak_bullets": [],
            "missing_sections": [],
            "cliches_found": [],
            "cover_letter": "",
        }
