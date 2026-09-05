"""
PRPCEM College Assistant - Large Intent System
60+ deterministic, rule-based intent recognition patterns without Machine Learning.
Enforces Intent-First Gatekeeping to ensure query intent is resolved BEFORE database searching.
"""

import re

# Comprehensive Intent Rules Taxonomy
INTENT_PATTERNS = {
    # -------------------------------------------------------------
    # 1. PLACEMENT & RECRUITER INTENTS - Requirement #7 & #11
    # -------------------------------------------------------------
    "placement_companies": [
        r"\b(which|what|list(\s+of)?)\s+(companies|recruiters|employers)\s+(come|visit|hire|recruit|arrive|coming|hiring|visiting)\b",
        r"\b(which|what)\s+companies\s+come\s+for\s+placement\b",
        r"\bcompanies\s+(visiting|coming|hiring)(\s+prpcem|\s+college|\s+campus)?\b",
        r"\bwhich\s+companies\s+(recruit|hire|visit)\s*(students)?\b",
        r"\bwhich\s+companies\s+come\b",
        r"\bcompanies\s+coming\s+to\s+college\b",
        r"\bcompanies\s+hiring\b",
        r"^placement\s+companies[?]?$",
        r"^recruiters[?]?$",
        r"^top\s+recruiters[?]?$",
        r"^companies[?]?$",
        r"\brecruiting\s+companies\b",
        r"\bwho\s+recruits\s+students\b",
        r"\bcompanies\s+coming\s+for\s+placement\b",
        r"\bcampus\s+recruiters\b"
    ],
    "placement_statistics": [
        r"\b(placement\s+statistics|placement\s+records|placement\s+report)\b",
        r"\b(highest\s+package|maximum\s+package|top\s+package)\b",
        r"\b(average\s+package|median\s+package|mean\s+package)\b",
        r"\bhow\s+are\s+the\s+placements\b",
        r"\btell\s+me\s+about\s+placements?\b",
        r"\bplacement\s+scenario\b",
        r"\bpackage\s+offered\b"
    ],
    "training_placement": [
        r"\btraining\s+and\s+placement\s*(cell|officer|dept)?\b",
        r"\btpo\b",
        r"\bplacement\s+cell\b",
        r"\btraining\s+officer\b"
    ],

    # -------------------------------------------------------------
    # 2. HOD & LEADERSHIP INTENTS - Requirement #4, #5 & #6
    # -------------------------------------------------------------
    "department_hod": [
        r"\bwho\s+is\s+(the\s+)?([a-z0-9\s\(\)\&\/\-]+)?\s*(hod|head\s+of\s+(the\s+)?department)\b",
        r"\bwho\s+(heads|leads)\s+(the\s+)?([a-z0-9\s\(\)\&\/\-]+)?\s*(department|branch)?\b",
        r"\b(tell\s+me\s+)?([a-z0-9\s\(\)\&\/\-]+)?\s*hod\b",
        r"\bhod\s+of\s+([a-z0-9\s\(\)\&\/\-]+)\b",
        r"\bhead\s+of\s+([a-z0-9\s\(\)\&\/\-]+)\s+department\b",
        r"\bwho\s+is\s+the\s+head\s+of\b",
        r"^hod[?]?$",
        r"^who\s+is\s+(the\s+)?hod[?]?$",
        r"\bdepartment\s+head\b"
    ],
    "chairman": [
        r"\bwho\s+is\s+(the\s+)?chairman\b",
        r"\bchairman\s*(name|sir)?\b",
        r"\bpravin\s+pote\s+patil\b",
        r"^chairman[?]?$",
        r"^who\s+is\s+(the\s+)?chairman[?]?$"
    ],
    "vice_chairman": [
        r"\bwho\s+is\s+(the\s+)?vice[\s\-]chairman\b",
        r"\bvice[\s\-]chairman\s*(name|sir)?\b",
        r"\bshreyash\s+pote\s+patil\b",
        r"^vice[\s\-]chairman[?]?$",
        r"^who\s+is\s+(the\s+)?vice[\s\-]chairman[?]?$"
    ],
    "director": [
        r"\bwho\s+is\s+(the\s+)?director(\s+of\s+prpcem|\s+of\s+college)?\b",
        r"\bdirector\s*(name|sir|dr)?\b",
        r"\bdr\.?\s*prakash\s+(m\.?)?\s*khodke\b",
        r"^director[?]?$",
        r"^who\s+is\s+(the\s+)?director[?]?$"
    ],
    "principal": [
        r"\bwho\s+is\s+(the\s+)?principal\b",
        r"\bprincipal\s*(name|sir|dr)?(?!\s*of\s+(?:dr|the|a))\b",
        r"\bprincipal\s+of\s+prpcem\b",
        r"\bdr\.?\s*p\.?\s*m\.?\s*jawandhi?ya\b",
        r"\bhead\s+of\s+(the\s+)?institute\b",
        r"^principal[?]?$",
        r"^who\s+is\s+(the\s+)?principal[?]?$"
    ],
    "vice_principal": [
        r"\bwho\s+is\s+(the\s+)?vice[\s\-]principal\b",
        r"\bvice[\s\-]principal\s*(name|dr)?\b",
        r"\bdr\.?\s*mohammad\s+zuhair\b",
        r"^vice[\s\-]principal[?]?$",
        r"^who\s+is\s+(the\s+)?vice[\s\-]principal[?]?$"
    ],
    "dean": [
        r"\bwho\s+is\s+(the\s+)?dean(\s+academics?|\s+of\s+academics?|\s+of\s+prpcem)?\b",
        r"\bdean\s+(of\s+)?academics?\b",
        r"\bdean\s+academic\s+office\b",
        r"\bdr\.?\s*v\.?\s*b\.?\s*kute\b",
        r"^dean[?]?$",
        r"^who\s+is\s+(the\s+)?dean[?]?$",
        r"\bdeans\b"
    ],
    "dean_academics": [
        r"\bwho\s+is\s+(the\s+)?dean\s+academics?\b",
        r"\bdean\s+(of\s+)?academics?\b",
        r"\bdean\s+academic\s+office\b",
        r"\bdr\.?\s*v\.?\s*b\.?\s*kute\b"
    ],
    "faculty_list": [
        r"\bfaculty\s+(members?|list|details|staff)\b",
        r"\bprofessors?\s+in\b",
        r"\bteaching\s+staff\b"
    ],

    # -------------------------------------------------------------
    # 3. COLLEGE ESTABLISHMENT & ABOUT - Requirement #4 & #22
    # -------------------------------------------------------------
    "college_establishment": [
        r"\b(when|what\s+year)\s+was\s+(prpcem|the\s+college)\s+(established|founded|started|built)\b",
        r"\byear\s+of\s+establishment\b",
        r"\bestablishment\s+year\b",
        r"\bwhen\s+did\s+(prpcem|the\s+college)\s+start\b",
        r"\bhistory\s+of\s+(prpcem|college)\b"
    ],
    "about_college": [
        r"\babout\s+(prpcem|college|pote\s+patil)\b",
        r"\bcollege\s+(overview|profile|vision|mission)\b",
        r"\bwho\s+is\s+prpcem\b",
        r"\bnaac\s+accreditation\b",
        r"\baicte\s+approval\b",
        r"\bdte\s+code\b",
        r"\bofficial\s+website\b"
    ],

    # -------------------------------------------------------------
    # 4. TIMING INTENTS - Requirement #11 & #12
    # -------------------------------------------------------------
    "college_timing": [
        r"\b(college|prpcem)?\s*(timings?|hours|schedule)\b",
        r"\bwhat\s+time\s+does\s+(college|prpcem)\s+(start|open|close|end)\b",
        r"\bwhen\s+does\s+(college|prpcem)\s+(start|open|close|end)\b",
        r"\bwhat\s+are\s+(the\s+)?(college|prpcem)\s*(working\s*)?hours\b",
        r"\bwhat\s+is\s+(the\s+)?(college|prpcem)\s*timing\b",
        r"\b(at\s+what\s+time\s+should\s+i\s+come\s+to\s+college)\b",
        r"\bcollege\s+start(ing)?\s+time\b",
        r"\bcollege\s+closing\s+time\b",
        r"^timing[s]?$",
        r"^college\s+timing[s]?$"
    ],
    "office_timing": [
        r"\b(admin|office|administrative)\s*(timing|hours|time)\b",
        r"\bwhen\s+does\s+the\s+office\s+(open|close)\b",
        r"\boffice\s+working\s+hours\b"
    ],
    "library_timing": [
        r"\blibrary\s*(timing|hours|time|reading\s*room)\b",
        r"\bwhen\s+does\s+(the\s+)?library\s+(open|close)\b"
    ],

    # -------------------------------------------------------------
    # 5. CUTOFFS & CAP ROUNDS - Requirement #4 & #25
    # -------------------------------------------------------------
    "cutoff": [
        r"\bcut[\s\-]?offs?\b",
        r"\bclosing\s+(rank|percentile|score|marks)\b",
        r"\bopening\s+(rank|percentile|score|marks)\b",
        r"\bwhat\s+is\s+(the\s+)?([a-z0-9\s\(\)\&\/\-]+)?\s*cut[\s\-]?off\b",
        r"\bpercentile\s+required\s+for\b",
        r"\bminimum\s+(marks|percentile)\s+for\b"
    ],
    "cap_round": [
        r"\bcap\s+rounds?\b",
        r"\bcentralized\s+admission\s+process\b",
        r"\bcap\s+allotment\b",
        r"\bspot\s+round\b"
    ],

    # -------------------------------------------------------------
    # 6. COURSES & DEPARTMENTS - Requirement #3 & #25
    # -------------------------------------------------------------
    "departments": [
        r"\b(which|what|list\s+of)?\s*departments?\s*(are\s+there|available|offered)?\b",
        r"\bwhich\s+branches\s+(are\s+there|available)\b",
        r"\blist\s+of\s+(departments|branches)\b",
        r"\bhow\s+many\s+departments\b"
    ],
    "courses": [
        r"\b(which|what|list\s+of)?\s*courses?\s*(offered|available|list)?\b",
        r"\bprogrammes?\s*(offered|available)?\b",
        r"\bdegrees?\b",
        r"\bwhat\s+can\s+i\s+study\b",
        r"\bbtech\s+branches\b"
    ],

    # -------------------------------------------------------------
    # 7. ADMISSIONS, DOCUMENTS, FEES & SCHOLARSHIPS - Requirement #3 & #25
    # -------------------------------------------------------------
    "admission_process": [
        r"\bhow\s+can\s+i\s+apply(\s+for\s+admission)?\b",
        r"\bhow\s+to\s+(apply|get\s+admission|take\s+admission|join)\b",
        r"\badmission\s+process\b",
        r"\badmission\s+procedure\b",
        r"\bhow\s+to\s+register\b"
    ],
    "eligibility": [
        r"\beligibility\s*(criteria)?\b",
        r"\bam\s+i\s+eligible\b",
        r"\bwho\s+can\s+apply\b",
        r"\bminimum\s+percentage\b",
        r"\bqualifying\s+exam\b"
    ],
    "documents": [
        r"\bwhat\s+documents\s+are\s+required\b",
        r"\bdocuments?\s*(required|needed|checklist)?\b",
        r"\bcertificates?\s*(required|needed)\b",
        r"\bdocument\s+verification\b"
    ],
    "fees": [
        r"\bfees?\s*(structure|details)?\b",
        r"\btuition\s*fees?\b",
        r"\bhow\s+much\s+(does\s+it\s+cost|is\s+the\s+fee)\b",
        r"\bfee\s+structure\b"
    ],
    "scholarship": [
        r"\bscholarships?\b",
        r"\bebc\s*(concession|scholarship)?\b",
        r"\btfws\b",
        r"\bfee\s+concession\b"
    ],

    # -------------------------------------------------------------
    # 8. ACADEMICS, SYLLABUS, CALENDAR & EXAMS - Requirement #3, #6, #25
    # -------------------------------------------------------------
    "syllabus": [
        r"\b(where\s+can\s+i\s+find\s+(the\s+)?)?syllabus\b",
        r"\bcourse\s+scheme\b",
        r"\bcurriculum\b",
        r"\bteaching\s+scheme\b"
    ],
    "academic_calendar": [
        r"\b(where\s+can\s+i\s+find\s+(the\s+)?)?academic\s+calendar\b",
        r"\bsemester\s+dates\b",
        r"\bterm\s+start\b",
        r"\bsemester\s+schedule\b"
    ],
    "examination": [
        r"\b(when\s+are\s+the\s+)?examinations?\b",
        r"\bexamination\s+process\b",
        r"\bexam\s+timetable\b",
        r"\bexamcell\b",
        r"\bsessional\s+exam\b",
        r"\bbacklog(s)?\b",
        r"\bresults?\b"
    ],

    # -------------------------------------------------------------
    # 9. STUDENT FACILITIES - Requirement #3, #6, #25
    # -------------------------------------------------------------
    "hostel": [
        r"\b(does\s+the\s+college\s+have\s+a\s+|is\s+there\s+a\s+|is\s+)?hostels?\s*(available)?\b",
        r"\baccommodation\b",
        r"\bboys\s+hostel\b",
        r"\bgirls\s+hostel\b"
    ],
    "library": [
        r"\b(is\s+there\s+a\s+|is\s+)?library\s*(available)?\b",
        r"\bcentral\s+library\b",
        r"\breading\s+room\b"
    ],
    "facilities": [
        r"\b(what\s+)?facilities\s*(are\s+available)?\b",
        r"\bcampus\s+amenities\b",
        r"\binfrastructure\b",
        r"\bsports\b",
        r"\bgym\b",
        r"\btransport\b",
        r"\bbus\b"
    ],

    # -------------------------------------------------------------
    # 10. CONTACT & LOCATION - Requirement #3, #6, #25
    # -------------------------------------------------------------
    "location": [
        r"\b(where\s+is|location\s+of|address\s+of|how\s+to\s+reach)\s+(the\s+)?(prpcem|college|campus)\b",
        r"\bwhere\s+is\s+prpcem\b",
        r"\bwhere\s+is\s+(the\s+)?college\s+located\b",
        r"\bcollege\s+(address|location)\b"
    ],
    "contact": [
        r"\bwhat\s+is\s+the\s+(college\s+)?contact\s*number\b",
        r"\bcontact\s*(number|details|info)?\b",
        r"\bphone\s*(number)?\b",
        r"\btelephone\b",
        r"\bhelpline\b",
        r"\bemail\s*(address)?\b"
    ]
}

def detect_intent(text):
    """
    Evaluates rule-based patterns against normalized user input.
    Returns (intent_name, confidence_score).
    Prioritizes specific compound intents (e.g. placement_companies, department_hod)
    over generic keyword occurrences.
    CRITICAL: Longer/more-specific phrases like "vice chairman" / "vice principal"
    are checked BEFORE their shorter sub-phrases like "chairman" / "principal".
    """
    cleaned = text.lower().strip()

    # Rule 1: Disambiguate Placement Companies (Requirement #6 & #7)
    company_triggers = ["companies", "company", "recruiter", "recruiters", "who recruits", "who visits", "who hires", "campus recruiters", "recruitment", "drive"]
    if any(w in cleaned for w in company_triggers):
        placement_qualifiers = ["placement", "recruit", "visit", "hire", "campus", "jobs", "students", "come", "coming", "hiring", "visiting", "drive", "arrival"]
        if any(w in cleaned for w in placement_qualifiers) or cleaned in ["companies", "companies?", "recruiters", "recruiters?", "placement companies", "top recruiters", "campus recruiters"]:
            return "placement_companies", 0.98

    # Rule 2: Disambiguate College Establishment (Requirement #4)
    if any(w in cleaned for w in ["established", "establishment", "founded", "what year was", "built in"]):
        if not any(w in cleaned for w in ["placement", "company", "companies", "recruit", "cutoff", "timing"]):
            return "college_establishment", 0.98

    # Rule 3: HOD queries (Requirement #5)
    if "hod" in cleaned or "head of department" in cleaned or "who heads" in cleaned or "head of the department" in cleaned or cleaned in ["hod", "hod?", "who is the hod", "who is the hod?"]:
        return "department_hod", 0.98

    # Rule 4: Leadership disambiguation — MUST check longer phrases first (Requirement #4)
    # "vice chairman" MUST NOT fall through to "chairman"
    # "vice principal" MUST NOT fall through to "principal"
    if "vice chairman" in cleaned or "vice-chairman" in cleaned:
        return "vice_chairman", 0.99
    if "vice principal" in cleaned or "vice-principal" in cleaned:
        return "vice_principal", 0.99
    if "dean" in cleaned:
        return "dean_academics", 0.98
    if "chairman" in cleaned:
        return "chairman", 0.98
    if "director" in cleaned and not ("physical education" in cleaned or "sports" in cleaned):
        return "director", 0.98
    if "principal" in cleaned:
        return "principal", 0.98

    # Rule 5: Timing Disambiguation (Requirement #9 & #17)
    if any(w in cleaned for w in ["timing", "timings", "hours", "schedule", "start time", "closing time", "opening time", "end time"]):
        if "library" in cleaned or "reading room" in cleaned:
            return "library_timing", 0.98
        if "office" in cleaned or "admin" in cleaned:
            return "office_timing", 0.98
        return "college_timing", 0.98
    if re.search(r"\b(what\s+time|when)\s+does\s+(the\s+)?(college|prpcem)\s+(start|open|close|end)\b", cleaned):
        return "college_timing", 0.98

    # Rule 6: Cutoff Queries (Requirement #4)
    if "cutoff" in cleaned or "cut off" in cleaned or "cut-off" in cleaned or "closing rank" in cleaned:
        return "cutoff", 0.96

    # Rule 7: About College (Requirement #1 & #25)
    if cleaned in ["about college", "tell me about college", "tell me about the college", "about prpcem", "tell me about prpcem", "overview", "college overview", "college profile"] or re.search(r"\babout\s+(prpcem|the\s+college|college)\b", cleaned):
        return "about_college", 0.98

    # Scan all taxonomy patterns
    best_intent = None
    best_matches = 0

    for intent, patterns in INTENT_PATTERNS.items():
        matches = sum(1 for pat in patterns if re.search(pat, cleaned))
        if matches > best_matches:
            best_matches = matches
            best_intent = intent

    if best_intent and best_matches > 0:
        return best_intent, min(0.6 + (best_matches * 0.15), 0.95)

    return "unknown", 0.0
