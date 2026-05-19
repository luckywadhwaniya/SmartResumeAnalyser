# Smart Resume Analyzer & Job Recommender

An AI-driven tool for resume analysis, skill extraction, and automated job matching.

## Features

- **Resume Analysis:** Constructive feedback on resume structure, impact, and content.
- **Job Matching:** Real-time job fetching from Adzuna, Remotive, and RemoteOK, filtered by candidate experience level.
- **Interview Preparation:** Generates behavioral and technical questions based on resume content, including an answer evaluation tool.
- **Skill Extraction:** NLP-based identification of technical and soft skills.
- **Document Processing:** PDF text extraction and automated cover letter generation.
- **UI:** Dark-themed dashboard with animated transitions.

## Technical Stack

- **Backend:** FastAPI
- **Frontend:** Vanilla JS / CSS / HTML
- **LLM:** Groq (Llama 3.3)
- **Parsing:** pdfplumber, spaCy
- **Data Sources:** Adzuna, Remotive, RemoteOK APIs

## Setup

### 1. Requirements
- Python 3.9+
- Groq API Key

### 2. Installation
```bash
git clone https://github.com/SMdaniyal687/resume_analyzer.git
cd resume_analyzer
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Environment Variables
Create a `.env` file in the root:
```env
GROQ_API_KEY=your_key
ADZUNA_APP_ID=optional_id
ADZUNA_APP_KEY=optional_key
```

### 4. Usage
```bash
python -m uvicorn main:app --reload
```
Access the application at `http://localhost:8000`.

## Project Structure
- `main.py`: Application entry point and API endpoints.
- `utils/`: Logic for PDF parsing, skill extraction, and LLM interaction.
- `static/`: Frontend assets.
- `requirements.txt`: Python dependencies.
