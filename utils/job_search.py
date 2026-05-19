import requests
import urllib.parse
import os

# JSearch API (RapidAPI) - Free tier, no credit card required
# Sign up at https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
# Then set your key as an environment variable: JSEARCH_API_KEY
JSEARCH_API_KEY = os.environ.get("JSEARCH_API_KEY", "")

def fetch_jobs(roles: list, experience_level: str = "Auto-Detect", location: str = "India") -> list:
    """
    Fetches real job listings using JSearch API (Google Jobs).
    Falls back to Smart Search Links if the API key is not configured.
    """
    
    if JSEARCH_API_KEY:
        return _fetch_from_jsearch(roles, experience_level, location)
    else:
        return _generate_smart_links(roles, experience_level, location)


def _fetch_from_jsearch(roles: list, experience_level: str, location: str) -> list:
    """Fetch real job listings from JSearch API."""
    jobs = []
    
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    # Map our experience levels to JSearch date parameters
    # We use only the first role to avoid burning API requests
    for role in roles[:1]:
        query = f"{role} in {location}"
        
        params = {
            "query": query,
            "page": "1",
            "num_pages": "1",
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("data", [])[:6]:
                    job_title = item.get("job_title", "Unknown Title")
                    employer = item.get("employer_name", "Unknown Company")
                    job_location = item.get("job_city", "") or item.get("job_country", location)
                    apply_link = item.get("job_apply_link", "") or item.get("job_google_link", "#")
                    
                    jobs.append({
                        "title": job_title,
                        "company": employer,
                        "location": job_location,
                        "link": apply_link
                    })
            else:
                print(f"JSearch API error: {response.status_code} - {response.text}")
                # Fall back to smart links on error
                return _generate_smart_links(roles, experience_level, location)
        except Exception as e:
            print(f"JSearch request failed: {e}")
            return _generate_smart_links(roles, experience_level, location)
    
    # If no results, fall back to smart links
    if not jobs:
        return _generate_smart_links(roles, experience_level, location)
        
    return jobs


def _generate_smart_links(roles: list, experience_level: str, location: str) -> list:
    """Fallback: Generate direct search links to LinkedIn and Indeed."""
    jobs = []
    
    level_query = ""
    if experience_level and experience_level != "Auto-Detect":
        level_query = experience_level.split("/")[0].strip() + " "
    
    for role in roles[:2]:
        search_term = role
        if level_query and level_query.lower() not in role.lower():
            search_term = f"{level_query}{role}"
        
        loc_encoded = urllib.parse.quote(location)
        role_encoded = urllib.parse.quote(search_term)
        
        jobs.append({
            "title": f"🔗 Search '{search_term}' on LinkedIn",
            "company": "LinkedIn",
            "location": location,
            "link": f"https://www.linkedin.com/jobs/search/?keywords={role_encoded}&location={loc_encoded}"
        })
        
        jobs.append({
            "title": f"🔗 Search '{search_term}' on Indeed",
            "company": "Indeed",
            "location": location,
            "link": f"https://www.indeed.com/jobs?q={role_encoded}&l={loc_encoded}"
        })
    
    return jobs
