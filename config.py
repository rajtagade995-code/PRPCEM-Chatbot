"""
PRPCEM College Assistant - Configuration
Official College Information Assistant for:
P. R. Pote Patil College of Engineering & Management, Amravati
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Official College Information
COLLEGE_NAME = "P. R. Pote Patil College of Engineering & Management"
COLLEGE_SHORT_NAME = "PRPCEM"
COLLEGE_WEBSITE = "https://prpotepatilengg.ac.in/"
COLLEGE_ACADEMICS_WEBSITE = "https://academics.prpotepatilengg.ac.in/"
COLLEGE_EXAMCELL_WEBSITE = "https://examcell.prpotepatilengg.ac.in/"
COLLEGE_LOCATION = "Pote Patil Educational Group, Pote Patil Road, Kathora, Amravati, (M.S.) India - 444604"
COLLEGE_DTE_CODE = "1107"

# Approved Crawler Domains & Subdomains
ALLOWED_DOMAINS = [
    "prpotepatilengg.ac.in",
    "www.prpotepatilengg.ac.in",
    "academics.prpotepatilengg.ac.in",
    "examcell.prpotepatilengg.ac.in"
]

# Web Crawler Settings
MAX_PAGES = 500
MAX_DEPTH = 5
REQUEST_TIMEOUT = 10
CRAWLER_USER_AGENT = "PRPCEM-College-Assistant"

# Database Settings
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "database", "chatbot.db"))
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")

# Data & PDF Storage
DATA_DIR = os.path.join(BASE_DIR, "data")
PDF_CACHE_DIR = os.path.join(DATA_DIR, "pdf_cache")
CRAWLED_PAGES_JSON = os.path.join(DATA_DIR, "crawled_pages.json")

# Application Security & Admin Setup
SECRET_KEY = os.environ.get("SECRET_KEY", "prpcem-rule-based-chatbot-secure-secret-key-2026")
DEFAULT_ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "adminpassword123")

# College Verified Defaults
DEFAULT_COLLEGE_TIMING = "10:30 AM to 5:50 PM"
DEFAULT_OFFICE_TIMING = "10:00 AM to 5:30 PM (Mon - Sat, 2nd & 4th Sat Off)"
DEFAULT_LIBRARY_TIMING = "8:30 AM to 6:00 PM (Mon - Sat)"
DEFAULT_EXAM_OFFICE_TIMING = "10:30 AM to 5:00 PM"
DEFAULT_ADMISSION_OFFICE_TIMING = "10:00 AM to 5:00 PM"
