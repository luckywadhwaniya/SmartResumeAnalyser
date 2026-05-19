import requests
import os

ADZUNA_APP_ID = os.environ.get("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.environ.get("ADZUNA_APP_KEY", "")


def fetch_jobs(roles: list, location: str = "India", skills: list = None) -> list:
    """
    Fetches real job listings from multiple free APIs with cascading fallback.
    Order: Adzuna → Remotive → RemoteOK.
    Returns up to 20 normalized job objects.
    """
    jobs = []

    # --- 1. Adzuna (if credentials present) ---
    if ADZUNA_APP_ID and ADZUNA_APP_KEY:
        for role in roles[:2]:
            try:
                adzuna_jobs = _fetch_adzuna(role, location)
                jobs.extend(adzuna_jobs)
            except Exception as e:
                print(f"[Adzuna] Failed for '{role}': {e}")

    # --- 2. Remotive (always free, no auth) ---
    if len(jobs) < 20:
        for role in roles[:2]:
            try:
                remotive_jobs = _fetch_remotive(role)
                jobs.extend(remotive_jobs)
            except Exception as e:
                print(f"[Remotive] Failed for '{role}': {e}")

    # --- 3. RemoteOK (always free, no auth, filter client-side) ---
    if len(jobs) < 20 and skills:
        try:
            remoteok_jobs = _fetch_remoteok(skills)
            jobs.extend(remoteok_jobs)
        except Exception as e:
            print(f"[RemoteOK] Failed: {e}")

    # --- 4. Legacy JSearch fallback ---
    jsearch_key = os.environ.get("JSEARCH_API_KEY", "")
    if len(jobs) < 5 and jsearch_key:
        for role in roles[:1]:
            try:
                jsearch_jobs = _fetch_jsearch(role, location, jsearch_key)
                jobs.extend(jsearch_jobs)
            except Exception as e:
                print(f"[JSearch] Failed: {e}")

    # Deduplicate by URL and cap at 20
    seen_urls = set()
    unique_jobs = []
    for job in jobs:
        if job["url"] not in seen_urls:
            seen_urls.add(job["url"])
            unique_jobs.append(job)
        if len(unique_jobs) >= 20:
            break

    return unique_jobs


# ─────────────────────── Adzuna ───────────────────────

def _fetch_adzuna(role: str, location: str) -> list:
    """Fetch from Adzuna API. Free tier: 250 requests/day."""
    # Adzuna uses country codes; map common names
    country_map = {
        "india": "in", "us": "us", "usa": "us", "uk": "gb",
        "canada": "ca", "australia": "au", "germany": "de",
    }
    country = country_map.get(location.lower().strip(), "in")

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": role,
        "results_per_page": 10,
        "content-type": "application/json",
    }

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("results", []):
        jobs.append({
            "title": item.get("title", "Unknown"),
            "company": item.get("company", {}).get("display_name", "Unknown"),
            "location": item.get("location", {}).get("display_name", location),
            "description": (item.get("description", "") or "")[:500],
            "url": item.get("redirect_url", "#"),
            "source": "adzuna",
        })
    return jobs


# ─────────────────────── Remotive ───────────────────────

def _fetch_remotive(role: str) -> list:
    """Fetch from Remotive API. Completely free, no auth."""
    url = "https://remotive.com/api/remote-jobs"
    params = {"search": role, "limit": 10}

    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("jobs", []):
        jobs.append({
            "title": item.get("title", "Unknown"),
            "company": item.get("company_name", "Unknown"),
            "location": item.get("candidate_required_location", "Remote"),
            "description": (item.get("description", "") or "")[:500],
            "url": item.get("url", "#"),
            "source": "remotive",
        })
    return jobs


# ─────────────────────── RemoteOK ───────────────────────

def _fetch_remoteok(skills: list) -> list:
    """Fetch from RemoteOK public JSON. No auth. Filter by skills."""
    url = "https://remoteok.com/remote-jobs.json"
    headers = {"User-Agent": "ResumeAnalyzer/1.0"}

    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    # First element is metadata, skip it
    listings = data[1:] if len(data) > 1 else []

    skills_lower = {s.lower() for s in skills}
    jobs = []

    for item in listings:
        tags = [t.lower() for t in item.get("tags", [])]
        # Check if any candidate skill appears in the job's tags
        if skills_lower.intersection(tags):
            jobs.append({
                "title": item.get("position", "Unknown"),
                "company": item.get("company", "Unknown"),
                "location": item.get("location", "Remote"),
                "description": (item.get("description", "") or "")[:500],
                "url": item.get("url", "#"),
                "source": "remoteok",
            })
            if len(jobs) >= 10:
                break

    return jobs


# ─────────────────────── JSearch (Legacy Fallback) ───────────────────────

def _fetch_jsearch(role: str, location: str, api_key: str) -> list:
    """Legacy fallback: JSearch via RapidAPI."""
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }
    params = {"query": f"{role} in {location}", "page": "1", "num_pages": "1"}

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for item in data.get("data", [])[:6]:
        jobs.append({
            "title": item.get("job_title", "Unknown"),
            "company": item.get("employer_name", "Unknown"),
            "location": item.get("job_city", "") or item.get("job_country", location),
            "description": (item.get("job_description", "") or "")[:500],
            "url": item.get("job_apply_link", "") or item.get("job_google_link", "#"),
            "source": "jsearch",
        })
    return jobs
