# utils/jd_matcher.py
from utils import llm

def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    """
    Compares a parsed resume against a specific Job Description.
    Returns an ATS score, matched/missing skills, and actionable advice.
    """
    prompt = f"""You are an elite Applicant Tracking System (ATS) and expert technical recruiter.

Perform a deep, strict comparison between the candidate's RESUME and the target JOB DESCRIPTION.

RESUME:
---
{resume_text[:4000]}
---

JOB DESCRIPTION:
---
{jd_text[:4000]}
---

Return ONLY a valid JSON object with these exact keys:
{{
  "ats_score": <int 0-100 based on keyword match, experience alignment, and formatting>,
  "matched_skills": ["<skill 1>", "<skill 2>"],
  "missing_skills": ["<critically missing skill 1>", "<critically missing skill 2>"],
  "culture_fit_analysis": "<2-3 sentences evaluating how well their soft skills/experience match the company's apparent culture/needs>",
  "bullet_suggestions": [
    {{
      "current_bullet": "<a weak or generic bullet from their resume>",
      "tailored_bullet": "<how to rewrite it to specifically target keywords in the JD>"
    }}
  ]
}}

Be brutal but fair. Do not hallucinate skills they don't have. Limit bullet_suggestions to 2 maximum.
"""

    try:
        return llm.ask_json(prompt)
    except Exception as e:
        return {
            "ats_score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "culture_fit_analysis": f"Analysis failed: {str(e)}",
            "bullet_suggestions": []
        }