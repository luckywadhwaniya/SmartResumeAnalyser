import json
import time
from utils import llm

# Numeric weight for each level — used to penalise mismatches
LEVEL_RANKS = {
    "internship": 0,
    "intern": 0,
    "entry level": 1,
    "entry": 1,
    "junior": 1,
    "mid-level": 2,
    "mid level": 2,
    "mid": 2,
    "senior": 3,
    "senior / lead": 3,
    "lead": 3,
    "staff": 3,
}


def match_and_rank(jobs: list, skills: list, experience_level: str, max_workers: int = 4) -> list:
    """
    Scores jobs in batches of 3 via Groq. Applies a level-mismatch penalty
    so that senior roles score much lower for junior/entry candidates.
    Returns top 6 jobs sorted by final score.
    """
    if not jobs:
        return []

    candidate_rank = _level_rank(experience_level)
    scored_jobs = []

    BATCH_SIZE = 3
    for i in range(0, len(jobs), BATCH_SIZE):
        batch = jobs[i:i + BATCH_SIZE]
        try:
            results = _score_batch(batch, skills, experience_level)
            for job, result in zip(batch, results):
                # Apply seniority penalty
                adjusted = _apply_level_penalty(result, job, candidate_rank)
                scored_jobs.append({**job, **adjusted})
        except Exception as e:
            print(f"[Matcher] Batch failed: {e}")
            for job in batch:
                scored_jobs.append({**job, **_default_score()})

        if i + BATCH_SIZE < len(jobs):
            time.sleep(1)

    scored_jobs.sort(key=lambda x: x.get("score", 0), reverse=True)
    return scored_jobs[:6]


def _score_batch(jobs: list, skills: list, experience_level: str) -> list:
    """Score multiple jobs in a single LLM call."""
    job_descriptions = ""
    for idx, job in enumerate(jobs):
        desc = (job.get("description", "") or "")[:200]
        job_descriptions += f"""
JOB {idx + 1}:
- Title: {job.get('title', 'N/A')}
- Company: {job.get('company', 'N/A')}
- Description: {desc}
"""

    prompt = f"""You are an expert job-matching system.

CANDIDATE:
- Skills: {', '.join(skills)}
- Experience Level: {experience_level}

Score each of these {len(jobs)} jobs for this candidate. Be STRICT about level fit — a Junior candidate should score low on Senior roles.

{job_descriptions}

Return ONLY a JSON array of {len(jobs)} objects IN ORDER. Each object:
{{
  "score": <int 0-100, penalise heavily if job level doesn't match candidate level>,
  "match_reasons": [<2-3 short strings>],
  "gaps": [<1-2 short strings>]
}}"""

    try:
        results = llm.ask_json(prompt)
        if isinstance(results, dict):
            for key in results:
                if isinstance(results[key], list):
                    results = results[key]
                    break
        if not isinstance(results, list):
            return [_default_score()] * len(jobs)
        while len(results) < len(jobs):
            results.append(_default_score())
        sanitized = []
        for r in results[:len(jobs)]:
            sanitized.append({
                "score": _clamp(r.get("score", 0), 0, 100),
                "match_reasons": r.get("match_reasons", [])[:3],
                "gaps": r.get("gaps", [])[:2],
            })
        return sanitized
    except Exception as e:
        print(f"[Matcher] Batch scoring error: {e}")
        return [_default_score()] * len(jobs)


def _apply_level_penalty(result: dict, job: dict, candidate_rank: int) -> dict:
    """
    Detects if a job title is too senior for the candidate and reduces score.
    Also adds a gap note if the level mismatch is severe.
    """
    title = (job.get("title", "") or "").lower()
    job_rank = _infer_job_rank(title)

    score = result.get("score", 0)
    gaps = list(result.get("gaps", []))

    rank_diff = job_rank - candidate_rank
    if rank_diff >= 2:
        # e.g. candidate is Entry Level, job is Senior — heavy penalty
        score = max(0, score - 45)
        if not any("experience" in g.lower() or "senior" in g.lower() for g in gaps):
            gaps.insert(0, "Role requires significantly more experience than candidate has")
    elif rank_diff == 1:
        # e.g. candidate is Entry, job is Mid-Level — light penalty
        score = max(0, score - 15)

    return {**result, "score": score, "gaps": gaps[:2]}


def _level_rank(level: str) -> int:
    return LEVEL_RANKS.get(level.lower().strip(), 1)


def _infer_job_rank(title: str) -> int:
    """Infer seniority rank from job title keywords."""
    if any(w in title for w in ["senior", "sr.", "sr ", "lead", "staff", "principal", "head of", "vp", "director"]):
        return 3
    if any(w in title for w in ["mid", "ii", "iii", "2", "3"]):
        return 2
    if any(w in title for w in ["junior", "jr.", "jr ", "entry", "associate", "intern", "graduate", "trainee", "apprentice"]):
        return 0
    return 1  # default: assume mid-ish


def _clamp(value, min_val, max_val):
    try:
        return max(min_val, min(int(value), max_val))
    except (TypeError, ValueError):
        return 0


def _default_score():
    return {"score": 0, "match_reasons": ["Could not evaluate"], "gaps": []}
