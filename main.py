from fastapi import FastAPI, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Optional
import uvicorn
import shutil
import os

from utils.pdf_parser import extract_text_from_pdf
from utils.skill_extractor import extract_skills
from utils.ai_feedback import get_ai_feedback
from utils.job_search import fetch_jobs
from utils.job_matcher import match_and_rank
from utils.resume_roaster import roast_resume
from utils.interview_coach import generate_interview_prep, evaluate_answer
from utils.jd_matcher import match_resume_to_jd

app = FastAPI()

# Mount the static directory
# //app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/match-jd")
async def match_jd_endpoint(
    resume_text: str = Form(...),
    jd_text: str = Form(...)
):
    if not resume_text or not jd_text:
        return {"error": "Both resume text and job description are required."}
        
    result = match_resume_to_jd(resume_text, jd_text)
    return result

@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("static/index.html")


@app.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(""),
    experience_level: Optional[str] = Form("Auto-Detect"),
    location: Optional[str] = Form("India"),
):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Parse PDF
        resume_text = extract_text_from_pdf(temp_file)
        if not resume_text:
            return {"error": "Failed to extract text from the PDF."}

        # 2. Extract Skills
        extracted_skills = extract_skills(resume_text)

        # 3. AI Feedback
        clean_role = target_role.strip() if target_role else ""
        feedback_data = get_ai_feedback(resume_text, extracted_skills, clean_role, experience_level)

        suggested_roles = feedback_data.get("suggested_roles", [])
        feedback_text = feedback_data.get("feedback", "No feedback generated.")
        predicted_level = feedback_data.get("predicted_level", experience_level)

        # 4. Fetch real jobs using Phase 2 Smart Queries
        roles_to_search = suggested_roles if suggested_roles else (
            [clean_role] if clean_role else ["Software Engineer"]
        )
        clean_location = location.strip() if location else "India"
        
        # CHANGED: Now passing extracted_skills into the search engine
        from utils.job_search import fetch_jobs
        raw_jobs = fetch_jobs(roles_to_search, extracted_skills, predicted_level, clean_location)

        # 5. LLM-powered matching & ranking
        level_for_matching = predicted_level if predicted_level != "Auto-Detect" else "Entry Level"
        matched_jobs = match_and_rank(raw_jobs, extracted_skills, level_for_matching)

        return {
            "skills": extracted_skills,
            "feedback": feedback_text,
            "suggested_roles": suggested_roles,
            "predicted_level": predicted_level,
            "jobs": matched_jobs,
            "resume_text": resume_text,  # Send back for session caching
        }
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


@app.post("/roast")
async def roast_endpoint(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(""),
    experience_level: Optional[str] = Form("Auto-Detect"),
):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resume_text = extract_text_from_pdf(temp_file)
        if not resume_text:
            return {"error": "Failed to extract text from the PDF."}

        clean_role = target_role.strip() if target_role else ""
        result = roast_resume(resume_text, clean_role, experience_level)
        return result
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


@app.post("/interview-prep")
async def interview_prep_endpoint(
    file: UploadFile = File(...),
    target_role: Optional[str] = Form(""),
    experience_level: Optional[str] = Form("Auto-Detect"),
):
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resume_text = extract_text_from_pdf(temp_file)
        if not resume_text:
            return {"error": "Failed to extract text from the PDF."}

        clean_role = target_role.strip() if target_role else ""
        result = generate_interview_prep(resume_text, clean_role, experience_level)
        result["resume_text"] = resume_text  # For answer evaluator
        return result
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)


@app.post("/evaluate-answer")
async def evaluate_answer_endpoint(
    question: str = Form(...),
    user_answer: str = Form(...),
    resume_text: str = Form(...),
):
    result = evaluate_answer(question, user_answer, resume_text)
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
