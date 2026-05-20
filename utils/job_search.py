# utils/job_search.py
import requests
import urllib.parse
import os
import random

JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY", "")

def generate_smart_queries(roles: list, skills: list, experience_level: str, location: str) -> list:
    """
    PHASE 2 LOGIC: Constructs highly targeted search queries based on skills, level, and location.
    """
    queries = []
    
    # Map raw experience to search-friendly terms
    level_map = {
        "Internship": "Intern",
        "Entry Level / Junior": "Junior OR Fresher OR Entry Level",
        "Mid-Level": "", # Mid-level usually doesn't need a keyword
        "Senior / Lead": "Senior OR Lead"
    }
    level_term = level_map.get(experience_level, "")

    # Grab the top 3 core technical skills to avoid overly narrow queries
    top_skills = " ".join(skills[:3]) if skills else ""

    # Generate a mix of queries to ensure we get broad and narrow results
    for role in roles[:2]:
        # Query 1: Skill-heavy (e.g., "React Node.js Junior jobs Ahmedabad")
        if top_skills:
            query_1 = f"{top_skills} {level_term} {role} jobs in {location}".strip()
            # Clean up extra spaces if level_term is empty
            query_1 = " ".join(query_1.split()) 
            queries.append(query_1)
        
        # Query 2: Traditional Role-based (Fallback)
        query_2 = f"{level_term} {role} jobs in {location}".strip()
        query_2 = " ".join(query_2.split())
        if query_2 not in queries:
            queries.append(query_2)

    return queries


def fetch_jobs(roles: list, skills: list, experience_level: str = "Auto-Detect", location: str = "India") -> list:
    """
    PHASE 1 LOGIC: Executes the smart queries against JSearch, falls back to Smart Links.
    """
    smart_queries = generate_smart_queries(roles, skills, experience_level, location)
    
    if JSEARCH_API_KEY:
        jobs = _fetch_from_jsearch(smart_queries)
        if jobs:
            return jobs
            
    # If API fails or is missing, generate direct LinkedIn/Indeed links
    return _generate_smart_links(smart_queries, location)


def _fetch_from_jsearch(queries: list) -> list:
    """Fetch real job listings using the generated smart queries."""
    jobs = []
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    # Execute the top query
    if not queries:
        return []
        
    target_query = queries[0]
    params = {
        "query": target_query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "month" # Keep results fresh
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            for item in data.get("data", [])[:10]: # Fetch up to 10 to give the Matcher room to rank
                jobs.append({
                    "title": item.get("job_title", "Unknown Title"),
                    "company": item.get("employer_name", "Unknown Company"),
                    "location": item.get("job_city", "") or item.get("job_country", "Unknown"),
                    "description": (item.get("job_description", "") or "")[:500],
                    "link": item.get("job_apply_link", "") or item.get("job_google_link", "#"),
                    "source": "jsearch"
                })
        else:
            print(f"[JSearch API Error] {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[JSearch Request Failed] {e}")
        
    return jobs


def _generate_smart_links(queries: list, location: str) -> list:
    """Generates direct search links if API data is unavailable."""
    jobs = []
    
    for query in queries[:2]:
        query_encoded = urllib.parse.quote(query)
        loc_encoded = urllib.parse.quote(location)
        
        jobs.append({
            "title": f"🔗 View LinkedIn Results for: {query}",
            "company": "LinkedIn",
            "location": location,
            "description": "Direct link to LinkedIn job search using your extracted skills and experience level.",
            "link": f"https://www.linkedin.com/jobs/search/?keywords={query_encoded}",
            "source": "linkedin"
        })
    
    return jobs