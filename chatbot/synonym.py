"""
PRPCEM College Assistant - Synonym System
Maps varied student terminology, colloquial phrasing, and jargon to canonical terms.
"""

SYNONYM_DICTIONARY = {
    "placement_companies": [
        "placement companies", "recruiters", "recruiting companies", "companies",
        "companies hiring", "companies visiting", "companies coming", "who recruits",
        "campus placement", "recruitment partners", "top recruiters", "campus recruiters"
    ],
    "department_hod": [
        "hod", "head of department", "head", "department head", "departmental head",
        "who heads", "hod sir", "hod madam", "head of the department"
    ],
    "timing": [
        "timing", "timings", "working hours", "college hours", "college timing",
        "hours", "time", "start time", "closing time", "opening time",
        "schedule", "when does college open", "when does college start"
    ],
    "admission": [
        "admission", "admissions", "apply", "application", "enrollment",
        "registration", "how to join", "intake", "seat allotment"
    ],
    "cutoff": [
        "cutoff", "cutoffs", "cut off", "cut-off", "closing rank", "opening rank",
        "merit list", "percentile", "score", "merit marks", "cap cutoff"
    ],
    "course": [
        "course", "courses", "programme", "program", "programmes", "degree",
        "branch", "branches", "discipline", "stream", "specialization"
    ],
    "fees": [
        "fee", "fees", "fee structure", "tuition", "tuition fee", "charges",
        "cost", "college expenses", "payment", "expenses"
    ],
    "hostel": [
        "hostel", "hostels", "accommodation", "residence", "dorm", "room",
        "stay", "boarding", "mess", "food"
    ],
    "library": [
        "library", "central library", "books", "reading room", "study room",
        "journals", "delnet", "e-library"
    ],
    "examination": [
        "exam", "exams", "examination", "examinations", "sessional", "unit test",
        "semester exam", "paper", "timetable", "results", "marks", "grade", "backlog"
    ],
    "contact": [
        "contact", "phone", "mobile", "telephone", "email", "address", "location",
        "reach", "helpline", "inquiry", "enquiry"
    ],
    "chairman": [
        "chairman", "president", "shri pravin pote", "pravin pote patil", "hon chairman", "trust chairman"
    ],
    "vice_chairman": [
        "vice chairman", "vice-chairman", "shreyash pote", "shreyash pote patil"
    ],
    "director": [
        "director", "dr prakash khodke", "prakash khodke", "director sir"
    ],
    "principal": [
        "principal", "principal sir", "dr jawandhiya", "p m jawandhiya", "head of institute"
    ],
    "vice_principal": [
        "vice principal", "vice-principal", "dr mohammad zuhair", "zuhair sir"
    ],
    "dean": [
        "dean", "dean academics", "dr v b kute", "v b kute", "dean academic", "deans"
    ],
    "facilities": [
        "facilities", "amenities", "infrastructure", "campus", "sports",
        "gym", "canteen", "bus", "transport", "labs"
    ],
    "college_establishment": [
        "established", "establishment", "founded", "started", "year of establishment",
        "establishment year", "history"
    ]
}

# Reverse lookup dictionary: token -> canonical term
REVERSE_SYNONYMS = {}
for canonical, synonyms in SYNONYM_DICTIONARY.items():
    for syn in synonyms:
        REVERSE_SYNONYMS[syn.lower()] = canonical

def get_canonical_term(term):
    """Returns the canonical root for any known synonym."""
    return REVERSE_SYNONYMS.get(term.lower().strip(), term.lower().strip())

def get_synonyms_for(term):
    """Returns all alternative synonym phrases for a canonical concept."""
    canonical = get_canonical_term(term)
    return SYNONYM_DICTIONARY.get(canonical, [term])
