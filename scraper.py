import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

KEYWORDS = [
    "communications", "communication", "public information", "media", "social media",
    "digital", "content", "video", "multimedia", "press", "advocacy", "outreach",
    "campaign", "partnerships", "external relations", "editorial", "writer", "producer",
    "information officer", "communications officer", "public information officer"
]

CATEGORY_RULES = {
    "Public Information": ["public information", "information officer", "press", "spokesperson"],
    "Digital / Social Media": ["digital", "social media", "content", "web", "online"],
    "Video / Multimedia": ["video", "multimedia", "producer", "visual", "photography"],
    "Advocacy / Outreach": ["advocacy", "outreach", "campaign", "engagement"],
    "Partnerships": ["partnership", "external relations", "donor"],
    "Communications": ["communication", "communications", "media", "editorial", "writer"],
}

SOURCES = [
    {"name": "UN Careers", "organization": "United Nations", "url": "https://careers.un.org/jobopening"},
    {"name": "UNDP Jobs", "organization": "UNDP", "url": "https://jobs.undp.org/cj_view_jobs.cfm"},
]

def normalize(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()

def is_relevant(text):
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in KEYWORDS)

def categorize(text):
    text_lower = text.lower()
    for category, words in CATEGORY_RULES.items():
        if any(word in text_lower for word in words):
            return category
    return "Communications"

def looks_new(posted_value):
    if not posted_value:
        return False
    today = datetime.now(timezone.utc).date()
    for fmt in ["%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y"]:
        try:
            return datetime.strptime(posted_value.strip(), fmt).date() >= today - timedelta(days=7)
        except ValueError:
            pass
    return False

def fetch_html(url):
    headers = {"User-Agent": "Mozilla/5.0 UN-Media-Jobs-Tracker/1.0", "Accept-Language": "en-US,en;q=0.9"}
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text

def extract_location(text):
    for word in ["New York", "Geneva", "Nairobi", "Vienna", "Rome", "Bangkok", "Paris", "Remote", "Home based", "Home-based", "Washington"]:
        if word.lower() in text.lower():
            return word
    return "Not listed"

def extract_level(text):
    match = re.search(r"\b(P-\d|D-\d|G-\d|NO-[A-D]|IICA-\d|LICA-\d|Internship|Consultant|Consultancy)\b", text, re.I)
    return match.group(0) if match else "Not listed"

def extract_deadline(text):
    patterns = [
        r"(?:deadline|closing date|expires|apply by)[:\s]+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})",
        r"(?:deadline|closing date|expires|apply by)[:\s]+([A-Za-z]+\s+[0-9]{1,2},\s+[0-9]{4})",
        r"(?:deadline|closing date|expires|apply by)[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1)
    return "Not listed"

def extract_posted_date(text):
    patterns = [
        r"(?:posted|date posted|publication date)[:\s]+([0-9]{1,2}\s+[A-Za-z]+\s+[0-9]{4})",
        r"(?:posted|date posted|publication date)[:\s]+([A-Za-z]+\s+[0-9]{1,2},\s+[0-9]{4})",
        r"(?:posted|date posted|publication date)[:\s]+([0-9]{4}-[0-9]{2}-[0-9]{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1)
    return ""

def scrape_generic_cards(source):
    jobs = []
    try:
        soup = BeautifulSoup(fetch_html(source["url"]), "html.parser")
    except Exception as exc:
        print(f"Could not fetch {source['name']}: {exc}")
        return jobs

    for link in soup.find_all("a", href=True):
        title = normalize(link.get_text(" "))
        if len(title) < 8:
            continue
        surrounding = normalize(link.parent.get_text(" ")) if link.parent else title
        combined = f"{title} {surrounding}"
        if not is_relevant(combined):
            continue
        job = {
            "title": title,
            "organization": source["organization"],
            "department": "",
            "location": extract_location(surrounding),
            "level": extract_level(surrounding),
            "deadline": extract_deadline(surrounding),
            "posted": extract_posted_date(surrounding),
            "category": categorize(combined),
            "source": source["name"],
            "link": urljoin(source["url"], link["href"]),
        }
        job["is_new"] = looks_new(job["posted"])
        jobs.append(job)
    return jobs

def dedupe_jobs(jobs):
    seen, clean = set(), []
    for job in jobs:
        key = (job["title"].lower(), job["organization"].lower(), job["link"])
        if key not in seen:
            seen.add(key)
            clean.append(job)
    return clean

def main():
    all_jobs = []
    for source in SOURCES:
        print(f"Scraping {source['name']}...")
        all_jobs.extend(scrape_generic_cards(source))
    jobs = dedupe_jobs(all_jobs)
    jobs.sort(key=lambda job: (not job.get("is_new", False), job.get("title", "")))
    Path("jobs.json").write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(jobs)} jobs to jobs.json")

if __name__ == "__main__":
    main()
