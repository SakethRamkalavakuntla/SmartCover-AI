import requests
from bs4 import BeautifulSoup

def scrape_job_description(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: Unable to fetch the job page (status code {response.status_code})"

        soup = BeautifulSoup(response.content, "html.parser")

        # Try common patterns used in job pages
        selectors = [
            {"tag": "div", "class": "job-description"},   # general
            {"tag": "section", "class": "job-description"},
            {"tag": "div", "id": "content"},
            {"tag": "main", "class": "main"},
            {"tag": "div", "class": "ats-description"},    # Greenhouse-style
        ]

        for sel in selectors:
            tag = soup.find(sel["tag"], class_=sel.get("class"), id=sel.get("id"))
            if tag:
                text = tag.get_text(separator=" ", strip=True)
                if len(text) > 200:
                    return text

        # Fallback: get the largest text blob (ignoring nav, footer)
        paragraphs = soup.find_all(["p", "li"])
        text_content = " ".join(p.get_text(strip=True) for p in paragraphs)
        return text_content.strip()

    except Exception as e:
        return f"Error: {str(e)}"
