"""
PRPCEM College Assistant - Relevance Scorer & Typo Corrector
Implements Levenshtein edit distance for typo tolerance and a transparent
multi-factor relevance scoring algorithm with negative penalties for contradictory categories (No ML).
"""

import re
from chatbot.synonym import get_canonical_term, get_synonyms_for


STOP_WORDS = {
    "what", "is", "the", "are", "for", "and", "you", "can", "tell", "how",
    "where", "who", "when", "which", "does", "did", "about", "there", "this",
    "that", "with", "from", "have", "has", "had", "will", "would", "should",
    "could", "all", "any", "some", "such", "than", "then", "into", "onto",
    "your", "mine", "their", "them", "they", "our", "ours", "please", "give",
    "know", "want", "like", "need", "show", "me", "to", "in", "at", "of", "on", "by",
    "college", "prpcem"
}

# Explicitly contradictory category pairings to prevent topic pollution
CONTRADICTORY_CATEGORIES = {
    "placement_companies": ["college_establishment", "about_college", "hostel", "college_timing", "examination",
                            "chairman", "vice_chairman", "director", "principal", "vice_principal", "dean", "dean_academics"],
    "placement_statistics": ["college_establishment", "about_college", "hostel", "college_timing",
                             "chairman", "vice_chairman", "director", "principal", "vice_principal", "dean", "dean_academics"],
    "college_establishment": ["placement_companies", "placement_statistics", "cutoff", "college_timing", "hostel"],
    "department_hod": ["college_establishment", "placement_companies", "hostel", "cutoff", "college_timing",
                       "chairman", "vice_chairman", "director", "principal", "vice_principal", "dean", "dean_academics"],
    "college_timing": ["placement_companies", "cutoff", "college_establishment", "hostel", "library_timing", "office_timing"],
    "library_timing": ["college_timing", "office_timing", "placement_companies", "cutoff"],
    "office_timing": ["college_timing", "library_timing", "placement_companies", "cutoff"],
    "cutoff": ["college_establishment", "department_hod", "hostel", "placement_companies"],
    "hostel": ["cutoff", "placement_companies", "college_establishment"],
    "library": ["cutoff", "placement_companies", "college_establishment"],
    # Leadership intents — strictly mutually contradictory (Requirement #4)
    "chairman": ["vice_chairman", "principal", "vice_principal", "director", "dean", "dean_academics", "department_hod",
                 "placement_companies", "college_establishment", "cutoff", "hostel"],
    "vice_chairman": ["chairman", "principal", "vice_principal", "director", "dean", "dean_academics", "department_hod",
                      "placement_companies", "college_establishment", "cutoff"],
    "director": ["chairman", "vice_chairman", "principal", "vice_principal", "dean", "dean_academics", "department_hod",
                 "placement_companies", "college_establishment", "cutoff"],
    "principal": ["chairman", "vice_chairman", "director", "vice_principal", "dean", "dean_academics", "department_hod",
                  "placement_companies", "college_establishment", "cutoff", "hostel"],
    "vice_principal": ["chairman", "vice_chairman", "director", "principal", "dean", "dean_academics", "department_hod",
                       "placement_companies", "college_establishment", "cutoff"],
    "dean": ["chairman", "vice_chairman", "director", "principal", "vice_principal", "department_hod",
             "placement_companies", "college_establishment", "cutoff"],
    "dean_academics": ["chairman", "vice_chairman", "director", "principal", "vice_principal", "department_hod",
                       "placement_companies", "college_establishment", "cutoff"],
}

def levenshtein_distance(s1, s2):
    """Computes exact edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

STANDARD_TERMS = [
    "college", "admission", "admissions", "placement", "placements",
    "department", "departments", "examination", "examinations",
    "cutoff", "cutoffs", "timing", "timings", "courses", "syllabus",
    "hostel", "library", "scholarship", "principal", "eligibility",
    "documents", "fees", "results", "recruiters", "companies", "company", "schedule",
    "electrical", "mechanical", "civil", "computer", "science"
]

PROTECTED_WORDS = {
    "coming", "hiring", "visiting", "recruiting", "working", "opening", "closing",
    "evening", "morning", "living", "taking", "making", "bring", "spring", "giving",
    "training", "meeting", "reading", "booking", "leaving", "starting", "ending",
    "having", "getting", "going", "doing", "holding", "standing"
}

def correct_typos(query_text):
    """Checks and corrects common misspellings using Levenshtein distance."""
    words = query_text.split()
    corrected_words = []

    for word in words:
        clean_word = re.sub(r"[^\w]", "", word).lower()
        if len(clean_word) <= 3 or clean_word in PROTECTED_WORDS:
            corrected_words.append(word)
            continue

        best_match = clean_word
        min_dist = float("inf")

        for standard in STANDARD_TERMS:
            if abs(len(standard) - len(clean_word)) > 2:
                continue

            dist = levenshtein_distance(clean_word, standard)
            max_allowed = 2 if (len(clean_word) >= 7 or clean_word in ["hostle"]) else 1

            if dist <= max_allowed and dist < min_dist:
                min_dist = dist
                best_match = standard

        corrected_words.append(best_match)

    return " ".join(corrected_words)

def score_document(query, doc_title, doc_headings, doc_content, doc_category, matched_intent=None, doc_dept=None, query_dept=None, doc_year=None, query_year=None):
    """
    Transparent rule-based relevance scoring with negative penalties:
    +10 exact intent match
    +8 exact question phrase match
    +7 entity match (department, role)
    +6 category match
    +5 title match
    +4 heading match
    +3 keyword match
    +3 synonym match
    +2 same department
    +2 same academic year
    -10 unrelated category
    -15 contradictory category
    -20 unrelated intent
    """
    score = 0
    query_norm = query.lower()
    query_tokens = [t for t in re.findall(r"\w+", query_norm) if len(t) > 2 and t not in STOP_WORDS]

    title_lower = (doc_title or "").lower()
    headings_lower = " ".join(doc_headings or []).lower() if isinstance(doc_headings, list) else (doc_headings or "").lower()
    content_lower = (doc_content or "").lower()
    category_lower = (doc_category or "").lower()
    dept_lower = (doc_dept or "").lower()

    # ---------------------------------------------------------
    # Negative Penalties for Contradictions (Requirement #10 & #22)
    # ---------------------------------------------------------
    if matched_intent:
        matched_intent_lower = matched_intent.lower()

        # -15 Contradictory Category penalty (instant rejection)
        if matched_intent_lower in CONTRADICTORY_CATEGORIES:
            contradictions = CONTRADICTORY_CATEGORIES[matched_intent_lower]
            if category_lower in contradictions:
                return -15  # Instant rejection

        # -20 Unrelated Intent mismatch for high-precision intents
        # These intents are so specific that any off-category match is wrong
        HIGH_PRECISION_INTENTS = {
            "placement_companies", "department_hod", "cutoff", "college_timing",
            "college_establishment", "chairman", "vice_chairman", "director",
            "principal", "vice_principal", "dean", "dean_academics",
            "library_timing", "office_timing"
        }
        if matched_intent_lower in HIGH_PRECISION_INTENTS:
            # Allow dean and dean_academics to match
            is_dean_match = (matched_intent_lower in ("dean", "dean_academics") and category_lower in ("dean", "dean_academics"))
            if category_lower and category_lower != matched_intent_lower and not is_dean_match:
                # Exception: HOD may share category with faculty
                if not (matched_intent_lower == "department_hod" and category_lower in ("departments", "faculty", "faculty_list")):
                    score -= 20

    # ---------------------------------------------------------
    # Positive Intent & Entity Scoring
    # ---------------------------------------------------------
    # +10 Exact Intent Match
    if matched_intent and (matched_intent.lower() == category_lower):
        score += 10

    # +8 Exact Question Phrase Match
    if query_norm in title_lower and len(query_norm) > 6:
        score += 8
    elif query_norm in content_lower and len(query_norm) > 8:
        score += 5

    # +7 Entity / Department Match
    if query_dept and doc_dept:
        if query_dept.lower() == doc_dept.lower():
            score += 7
        elif query_dept.lower() in doc_dept.lower() or doc_dept.lower() in query_dept.lower():
            score += 5
        else:
            # Different department specified -> penalty!
            score -= 15

    # +2 Same Academic Year
    if query_year and doc_year:
        if str(query_year) in str(doc_year):
            score += 2

    # +6 Category Match
    if matched_intent and matched_intent.lower() in category_lower:
        score += 6

    # ---------------------------------------------------------
    # Token-level Keyword and Synonym Scoring
    # ---------------------------------------------------------
    has_token_match = False
    for token in query_tokens:
        # +5 Title match
        if re.search(r"\b" + re.escape(token) + r"\b", title_lower):
            score += 5
            has_token_match = True

        # +4 Heading match
        if re.search(r"\b" + re.escape(token) + r"\b", headings_lower):
            score += 4
            has_token_match = True

        # +3 Exact keyword in content
        if re.search(r"\b" + re.escape(token) + r"\b", content_lower):
            score += 3
            has_token_match = True

        # +3 Synonym match
        synonyms = get_synonyms_for(token)
        for syn in synonyms:
            if syn != token and re.search(r"\b" + re.escape(syn) + r"\b", content_lower):
                score += 3
                has_token_match = True
                break

    # If query had substantial tokens but none matched this record:
    if query_tokens and not has_token_match and score <= 10:
        score -= 10  # Unrelated category penalty

    return score
