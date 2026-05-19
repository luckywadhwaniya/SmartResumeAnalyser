import spacy
import re

# Attempt to load spaCy model, but we don't strictly require it if it's not downloaded yet
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

# A foundational list of tech and soft skills
COMMON_SKILLS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "angular", "vue", "node.js",
    "sql", "nosql", "mongodb", "postgresql", "mysql", "machine learning", "deep learning", "nlp", 
    "computer vision", "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux", "html", "css",
    "django", "flask", "fastapi", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "data analysis", "data visualization", "tableau", "power bi", "agile", "scrum", "problem solving",
    "communication", "teamwork", "leadership"
]

def extract_skills(text: str) -> list:
    """
    Extracts skills from text using keyword matching and optional spaCy processing.
    """
    text_lower = text.lower()
    extracted = set()
    
    # 1. Regex/Keyword matching against our known dictionary
    for skill in COMMON_SKILLS:
        # Match whole words to avoid partial matches (e.g., 'c' in 'cat')
        # We need to escape because of things like c++
        pattern = r'\b' + re.escape(skill) + r'(?!\w)'
        if re.search(pattern, text_lower):
            # Capitalize properly for display
            extracted.add(skill.title() if skill not in ["aws", "gcp", "sql", "nlp"] else skill.upper())
            
    # 2. Optional: spaCy NLP for further entity extraction
    if nlp:
        doc = nlp(text)
        # In a more advanced version, we could use NER to find custom skills or education
        # for ent in doc.ents:
        #     if ent.label_ == "ORG": ...
        
    return list(extracted)
