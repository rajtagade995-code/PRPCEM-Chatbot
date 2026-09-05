"""
PRPCEM College Assistant - Text Cleaner
Sanitizes raw HTML, normalizes text, strips boilerplate, and classifies categories.
"""

import re
import hashlib
import html

class TextCleaner:
    @staticmethod
    def clean_html(html_content):
        """Strips scripts, styles, SVGs, and returns clean extracted text with preserved structure."""
        if not html_content:
            return ""

        # Remove scripts, styles, iframes, and meta
        cleaned = re.sub(r"<(script|style|svg|iframe|noscript)[^>]*>.*?</\1>", " ", html_content, flags=re.DOTALL | re.IGNORECASE)
        # Convert break tags and paragraph tags to newlines
        cleaned = re.sub(r"<(br|p|div|h[1-6]|li)[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
        # Remove remaining tags
        cleaned = re.sub(r"<[^>]+>", " ", cleaned)
        # Decode HTML entities
        cleaned = html.unescape(cleaned)
        # Normalize whitespace while preserving essential line breaks
        lines = [re.sub(r"\s+", " ", line).strip() for line in cleaned.splitlines()]
        filtered_lines = [l for l in lines if l and len(l) > 2]

        return "\n".join(filtered_lines)

    @staticmethod
    def normalize_whitespace(text):
        """Collapses duplicate whitespace into a single space."""
        if not text:
            return ""
        return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def compute_hash(text):
        """Computes SHA-256 hash of text for change detection."""
        if not text:
            return ""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def categorize_text(text, url=""):
        """Classifies text into a standard college category based on rule-based keyword matching."""
        combined = f"{url} {text}".lower()

        if any(w in combined for w in ["cutoff", "cap round", "admission", "eligibility", "fees", "fee structure", "merit"]):
            return "Admissions"
        elif any(w in combined for w in ["placement", "recruiters", "salary", "t&p", "training", "internship", "campus drive"]):
            return "Career & Placements"
        elif any(w in combined for w in ["syllabus", "curriculum", "courses", "department", "computer science", "mechanical", "civil", "electrical", "aiml", "mca", "mba"]):
            return "Academics"
        elif any(w in combined for w in ["exam", "examination", "timetable", "sessional", "backlog", "result", "sgbau"]):
            return "Examination"
        elif any(w in combined for w in ["hostel", "library", "sports", "gym", "canteen", "transport", "bus", "wifi", "labs"]):
            return "Student Facilities"
        elif any(w in combined for w in ["timing", "timings", "contact", "address", "principal", "about", "vision", "mission"]):
            return "College Information"
        else:
            return "General College Info"
