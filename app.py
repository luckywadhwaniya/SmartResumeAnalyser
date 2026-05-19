import streamlit as st
from utils.skill_extractor import extract_skills
from utils.ai_feedback import get_ai_feedback
from utils.job_search import fetch_jobs

st.set_page_config(page_title="Smart Resume Analyzer", layout="wide")

st.title("📄 Smart Resume Analyzer & Job Recommender")
st.markdown("Upload your resume to get instant feedback, extracted skills, and job recommendations powered by AI.")

# Sidebar configuration
with st.sidebar:
    st.header("Settings")
    target_role = st.selectbox(
        "Target Role",
        ["Data Analyst", "Software Engineer", "Product Manager", "Machine Learning Engineer"]
    )
    st.markdown("---")
    st.markdown("**Note:** Ensure your local Ollama instance is running for AI feedback.")

uploaded_file = st.file_uploader("Upload your Resume (PDF only)", type=["pdf"])

if uploaded_file is not None:
    st.info("Resume uploaded successfully! Processing...")
    
    # 1. Parse PDF
    with st.spinner("Extracting text from PDF..."):
        resume_text = extract_text_from_pdf(uploaded_file)
    
    if not resume_text:
        st.error("Failed to extract text from the PDF. Please try another file.")
    else:
        st.success("Text extracted successfully!")
        
        with st.expander("View Extracted Text"):
            st.text(resume_text[:1000] + "...\n[Text truncated for display]")
            
        st.write("---")
        
        # 2. Extract Skills
        with st.spinner("Analyzing skills..."):
            extracted_skills = extract_skills(resume_text)
            
        st.subheader("🛠️ Extracted Skills")
        if extracted_skills:
            st.write(", ".join([f"`{skill}`" for skill in extracted_skills]))
        else:
            st.warning("No standard tech skills detected. Make sure your resume highlights specific tools and languages.")
            
        col1, col2 = st.columns(2)
        
        # 3. AI Feedback (Ollama)
        with col1:
            st.subheader("🤖 AI Resume Feedback")
            with st.spinner(f"Generating feedback for {target_role} role via Ollama..."):
                feedback = get_ai_feedback(resume_text, extracted_skills, target_role)
            st.markdown(feedback)
            
        # 4. Job Recommendations
        with col2:
            st.subheader("💼 Live Job Recommendations")
            with st.spinner("Fetching relevant jobs..."):
                jobs = fetch_jobs(target_role)
                
            for job in jobs:
                st.markdown(f"""
                **[{job['title']}]({job['link']})**  
                *🏢 {job['company']} | 📍 {job['location']}*
                """)

