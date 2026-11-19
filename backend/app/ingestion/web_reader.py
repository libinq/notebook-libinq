import re
import httpx
from bs4 import BeautifulSoup
from typing import Tuple

def extract_web_content(url: str) -> Tuple[str, str]:
    """
    Fetch webpage, remove clutter, and extract main content as clean text.
    Returns (title, content).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    with httpx.Client(timeout=15.0, follow_redirects=True, headers=headers) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")

    # Extract title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text().strip()
    if not title:
        title = url

    # Remove unwanted tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe", "svg"]):
        tag.decompose()

    # Search for main article element
    main_el = soup.find("article") or soup.find("main") or soup.find(id=re.compile(r"content|main|article", re.I)) or soup.find(class_=re.compile(r"content|main|article|post", re.I)) or soup.body

    if not main_el:
        main_el = soup

    lines = []
    for elem in main_el.find_all(["h1", "h2", "h3", "h4", "p", "li", "pre", "blockquote"]):
        text = elem.get_text().strip()
        if text:
            if elem.name.startswith("h"):
                level = int(elem.name[1])
                lines.append(f"\n{'#' * level} {text}\n")
            elif elem.name == "li":
                lines.append(f"- {text}")
            elif elem.name == "blockquote":
                lines.append(f"> {text}")
            else:
                lines.append(f"\n{text}")

    body_text = "\n".join(lines).strip()
    if not body_text:
        body_text = main_el.get_text(separator="\n", strip=True)

    # Normalize whitespace
    body_text = re.sub(r'\n{3,}', '\n\n', body_text)
    return title, body_text
