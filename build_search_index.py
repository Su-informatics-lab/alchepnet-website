#!/usr/bin/env python3
"""
Build searchIndex.json for AlcHepNet website search functionality.
Indexes all active HTML pages (excludes backups, templates, and components).
"""

import os
import re
import json
from pathlib import Path

SRC_DIR = Path(__file__).parent / "src"
OUTPUT_FILE = SRC_DIR / "searchIndex.json"
PUBLICATIONS_JSON = SRC_DIR / "Publishing" / "doc" / "all_publications.json"
PUBLICATIONS_URL = "Publishing/publications.html"

# Pages to exclude from index
EXCLUDE_PATTERNS = [
    r"\.backup",
    r"-backup\.html$",
    r"\.bk\.html$",
    r"-bk\.html$",
    r"navbar\.html$",
    r"footer\.html$",
    r"search-modal\.html$",
    r"template",
    r"page-template",
]


def should_exclude(filepath: Path) -> bool:
    """Check if file should be excluded from index."""
    name = filepath.name
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    return False


def strip_html(html: str) -> str:
    """Remove HTML tags and decode entities."""
    # Remove script and style blocks
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove all HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_title(html: str, filepath: Path) -> str:
    """Extract page title from HTML."""
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    if match:
        return strip_html(match.group(1))
    # Fallback: use filename
    return filepath.stem.replace("-", " ").title()


def extract_content(html: str) -> str:
    """Extract main content from HTML for indexing."""
    # Prefer main tag content
    match = re.search(r"<main[^>]*>(.*?)</main>", html, re.DOTALL | re.IGNORECASE)
    if match:
        return strip_html(match.group(1))
    # Fallback: body content
    match = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL | re.IGNORECASE)
    if match:
        body = match.group(1)
        body = re.sub(r"<script[^>]*>.*?</script>", " ", body, flags=re.DOTALL | re.IGNORECASE)
        return strip_html(body)
    return ""


def get_relative_url(filepath: Path) -> str:
    """Get URL relative to src directory."""
    rel = filepath.relative_to(SRC_DIR)
    return str(rel).replace("\\", "/")


def load_publications_index_entries():
    """Create search entries from the publications JSON data."""
    if not PUBLICATIONS_JSON.exists():
        return []

    try:
        with open(PUBLICATIONS_JSON, "r", encoding="utf-8") as f:
            publications_data = json.load(f)
    except Exception as e:
        print(f"Warning: Could not read publications JSON {PUBLICATIONS_JSON}: {e}")
        return []

    publications_by_year = publications_data.get("publicationsByYear", {})
    entries = []

    for year in sorted(publications_by_year.keys(), reverse=True):
        publications = publications_by_year.get(year, [])
        if not publications:
            continue

        publication_texts = [
            pub.get("content", "").strip()
            for pub in publications
            if pub.get("content", "").strip()
        ]
        if not publication_texts:
            continue

        content = f"AlcHepNet Publications {year}. " + " ".join(publication_texts)
        snippet = " ".join(publication_texts[:2])
        if len(snippet) > 250:
            snippet = snippet[:250] + "..."

        entries.append({
            "title": f"AlcHepNet Publications ({year})",
            "url": PUBLICATIONS_URL,
            "snippet": snippet,
            "content": content,
        })

    return entries


def build_index():
    """Build search index from all HTML files."""
    index = []

    for html_file in sorted(SRC_DIR.rglob("*.html")):
        if should_exclude(html_file):
            continue

        try:
            with open(html_file, "r", encoding="utf-8", errors="ignore") as f:
                html = f.read()
        except Exception as e:
            print(f"Warning: Could not read {html_file}: {e}")
            continue

        title = extract_title(html, html_file)
        content = extract_content(html)

        if not content:
            content = title  # Ensure something to search

        snippet = content[:250] + "..." if len(content) > 250 else content

        index.append({
            "title": title,
            "url": get_relative_url(html_file),
            "snippet": snippet,
            "content": content,
        })

    index.extend(load_publications_index_entries())

    return index


def main():
    print("Building search index...")
    index = build_index()
    print(f"Indexed {len(index)} pages")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
