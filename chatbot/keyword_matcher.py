"""
PRPCEM College Assistant - Keyword Matcher & Entity Extractor
Normalizes input, extracts academic departments, administration roles,
reservation categories, and CAP rounds.
"""

import re

# Standard Department mapping supporting all abbreviations and variations
DEPARTMENT_MAP = {
    # CSE AIML (Priority over generic CSE)
    "cse aiml": "CSE (Artificial Intelligence and Machine Learning)",
    "cse-aiml": "CSE (Artificial Intelligence and Machine Learning)",
    "cse(aiml)": "CSE (Artificial Intelligence and Machine Learning)",
    "cse ai ml": "CSE (Artificial Intelligence and Machine Learning)",
    "cse ai and ml": "CSE (Artificial Intelligence and Machine Learning)",
    "cse ai & ml": "CSE (Artificial Intelligence and Machine Learning)",
    "cse-ai-ml": "CSE (Artificial Intelligence and Machine Learning)",
    "cse artificial intelligence": "CSE (Artificial Intelligence and Machine Learning)",
    "cse artificial intelligence and machine learning": "CSE (Artificial Intelligence and Machine Learning)",
    "computer science and engineering aiml": "CSE (Artificial Intelligence and Machine Learning)",
    "computer science and engineering ai and ml": "CSE (Artificial Intelligence and Machine Learning)",
    "computer science aiml": "CSE (Artificial Intelligence and Machine Learning)",
    "computer science ai and ml": "CSE (Artificial Intelligence and Machine Learning)",
    "ai and ml": "CSE (Artificial Intelligence and Machine Learning)",
    "ai & ml": "CSE (Artificial Intelligence and Machine Learning)",
    "ai ml": "CSE (Artificial Intelligence and Machine Learning)",
    "ai-ml": "CSE (Artificial Intelligence and Machine Learning)",
    "aiml": "CSE (Artificial Intelligence and Machine Learning)",
    "artificial intelligence and machine learning": "CSE (Artificial Intelligence and Machine Learning)",
    "artificial intelligence & machine learning": "CSE (Artificial Intelligence and Machine Learning)",

    # AI & DS
    "ai and ds": "Artificial Intelligence and Data Science",
    "ai & ds": "Artificial Intelligence and Data Science",
    "ai and data science": "Artificial Intelligence and Data Science",
    "ai & data science": "Artificial Intelligence and Data Science",
    "ai ds": "Artificial Intelligence and Data Science",
    "ai-ds": "Artificial Intelligence and Data Science",
    "ai&ds": "Artificial Intelligence and Data Science",
    "aids": "Artificial Intelligence and Data Science",
    "artificial intelligence and data science": "Artificial Intelligence and Data Science",
    "artificial intelligence & data science": "Artificial Intelligence and Data Science",
    "data science": "Artificial Intelligence and Data Science",

    # CSE
    "computer science and engineering": "Computer Science and Engineering",
    "computer science & engineering": "Computer Science and Engineering",
    "computer science": "Computer Science and Engineering",
    "computer engineering": "Computer Science and Engineering",
    "cse": "Computer Science and Engineering",
    "cs": "Computer Science and Engineering",
    "computer": "Computer Science and Engineering",

    # EXTC
    "electronics and telecommunication engineering": "Electronics and Telecommunication Engineering",
    "electronics & telecommunication engineering": "Electronics and Telecommunication Engineering",
    "electronics and telecommunication": "Electronics and Telecommunication Engineering",
    "electronics & telecommunication": "Electronics and Telecommunication Engineering",
    "electronics engineering": "Electronics and Telecommunication Engineering",
    "extc": "Electronics and Telecommunication Engineering",
    "entc": "Electronics and Telecommunication Engineering",
    "etc": "Electronics and Telecommunication Engineering",
    "e&tc": "Electronics and Telecommunication Engineering",
    "e and tc": "Electronics and Telecommunication Engineering",
    "electronics": "Electronics and Telecommunication Engineering",

    # Electrical
    "electrical engineering": "Electrical Engineering",
    "electrical engg": "Electrical Engineering",
    "electrical": "Electrical Engineering",
    "ee": "Electrical Engineering",

    # Mechanical
    "mechanical engineering": "Mechanical Engineering",
    "mechanical engg": "Mechanical Engineering",
    "mech engineering": "Mechanical Engineering",
    "mech engg": "Mechanical Engineering",
    "mechanical": "Mechanical Engineering",
    "mech": "Mechanical Engineering",
    "me": "Mechanical Engineering",

    # Civil
    "civil engineering": "Civil Engineering",
    "civil engg": "Civil Engineering",
    "civil": "Civil Engineering",
    "ce": "Civil Engineering",

    # Applied Science & Humanities (AS&H / First Year)
    "applied science and humanities": "Applied Science & Humanities",
    "applied science & humanities": "Applied Science & Humanities",
    "applied sciences": "Applied Science & Humanities",
    "applied science": "Applied Science & Humanities",
    "first year engineering": "Applied Science & Humanities",
    "first year": "Applied Science & Humanities",
    "ash": "Applied Science & Humanities",
    "as&h": "Applied Science & Humanities",
    "as & h": "Applied Science & Humanities",
    "fy": "Applied Science & Humanities",

    # Post Graduate
    "master of business administration": "MBA",
    "department of management studies": "MBA",
    "management studies": "MBA",
    "management": "MBA",
    "mba": "MBA",
    "master of computer applications": "MCA",
    "department of computer applications": "MCA",
    "computer applications": "MCA",
    "mca": "MCA"
}

CATEGORIES = [
    "OPEN", "OBC", "SC", "ST", "EWS", "TFWS",
    "VJ", "NT-A", "NT-B", "NT-C", "NT-D", "SEBC", "SBC"
]

def normalize_text(text):
    """Lowers text, strips punctuation, collapses whitespace."""
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s\-\&\(\)]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_entities(text):
    """
    Extracts structured entities from user query:
    department, role, category, cap_round, year, is_latest.
    """
    cleaned = text.lower()
    entities = {
        "department": None,
        "department_canonical": None,
        "role": None,
        "category": None,
        "cap_round": None,
        "year": None,
        "is_latest": False
    }

    # Detect if user explicitly asks for "latest"
    if any(w in cleaned for w in ["latest", "recent", "newest", "last year", "current"]):
        entities["is_latest"] = True

    # Extract Year (e.g. 2025-26, 2025, 2024, 2023)
    year_match = re.search(r"\b(202[0-9])(?:[\-\/](2[0-9]))?\b", cleaned)
    if year_match:
        full_match = year_match.group(0)
        if "-" in full_match:
            entities["year"] = full_match
        else:
            base_year = int(year_match.group(1))
            next_yr = str(base_year + 1)[-2:]
            entities["year"] = f"{base_year}-{next_yr}"

    # Extract CAP Round (e.g. CAP Round 1, CAP 2, Round 3, Spot Round)
    round_match = re.search(r"\b(?:cap\s*(?:round)?|round)\s*([1-4]|one|two|three|four)\b", cleaned)
    if round_match:
        raw_val = round_match.group(1)
        word_map = {"one": 1, "two": 2, "three": 3, "four": 4}
        entities["cap_round"] = word_map.get(raw_val, int(raw_val) if raw_val.isdigit() else 1)
    elif "spot" in cleaned:
        entities["cap_round"] = 4

    # Extract Category (OPEN, OBC, SC, ST, EWS, TFWS, etc.)
    for cat in CATEGORIES:
        cat_lower = cat.lower()
        if re.search(r"\b" + re.escape(cat_lower) + r"\b", cleaned):
            entities["category"] = cat
            break

    # Extract Role (Requirement #4: Separation of all leadership roles)
    if "vice chairman" in cleaned or "vice-chairman" in cleaned:
        entities["role"] = "Vice Chairman"
    elif "chairman" in cleaned:
        entities["role"] = "Chairman"
    elif "director" in cleaned:
        entities["role"] = "Director"
    elif "vice principal" in cleaned or "vice-principal" in cleaned:
        entities["role"] = "Vice Principal"
    elif "dean" in cleaned:
        entities["role"] = "Dean"
    elif "principal" in cleaned:
        entities["role"] = "Principal"
    elif "hod" in cleaned or "head of department" in cleaned or "who heads" in cleaned:
        entities["role"] = "HOD"

    # Extract Department (sort by length descending to match 'cse aiml' before 'cse')
    for alias in sorted(DEPARTMENT_MAP.keys(), key=len, reverse=True):
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, cleaned):
            entities["department"] = alias
            entities["department_canonical"] = DEPARTMENT_MAP[alias]
            break

    return entities
