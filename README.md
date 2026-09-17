# PRPCEM College Assistant
> **Official College Information Assistant**  
> **P. R. Pote Patil College of Engineering & Management, Amravati**  
> *Rule-Based College Information Assistant • Zero Machine Learning • Zero Paid APIs*

---

## 1. Project Introduction
**PRPCEM College Assistant** is a complete, standalone, professional, rule-based college information chatbot and web crawler system built for **P. R. Pote Patil College of Engineering & Management (PRPCEM), Amravati** (Official website: [https://prpotepatilengg.ac.in/](https://prpotepatilengg.ac.in/)).

It enables prospective and enrolled students, parents, and faculty to find verified, accurate, and up-to-date college information regarding:
- **Verified College Timing**: Strictly `10:30 AM to 5:50 PM`
- **Segregated Timings**: Distinct timings for Central Library (`8:30 AM – 6:00 PM`), Administrative Office (`10:00 AM – 5:30 PM`), and Admission / Exam Cells
- **Year-Wise & CAP Round Cutoffs**: Full cutoff system by Academic Year (`2025-26`, `2024-25`), Branch (CSE, AIML, AI&DS, Civil, Mech, EE, EXTC), Category (OPEN, OBC, SC, ST, EWS, TFWS), and CAP Rounds (1, 2, 3, Spot Round) with interactive Cutoff UI cards and official disclaimers
- **Admissions, Eligibility, Required Documents, and Fee Concessions**
- **Departments & Programmes**: Undergraduate B.Tech, Postgraduate MBA, MCA, M.Tech
- **Examinations, SGBAU timetables, and backlogs**
- **Placements & Recruiters**: TCS, Infosys, Cognizant, Wipro, salary packages, and T&P contacts
- **Campus Facilities**: Separate Boys & Girls Hostels, Digital Library, Sports complex, and Bus transport

---

## 2. Key Architecture & Principles

### Strictly Traditional Programming (Zero ML / No AI APIs)
This application contains:
- ❌ **NO Machine Learning**
- ❌ **NO Deep Learning / Neural Networks**
- ❌ **NO OpenAI / ChatGPT API**
- ❌ **NO Gemini / Claude / LLM APIs**
- ❌ **NO Paid APIs or AI Cloud Services**

The engine is engineered with traditional deterministic computer science:
```
WEB CRAWLER (Main Site + Academics Subdomain + Examcell Subdomain)
                   │
                   ▼
       STRUCTURED TEXT & TABLE EXTRACTION (HTML Tables + PDF Text)
                   │
                   ▼
      LOCAL SQLITE DATABASE (Knowledge + Cutoffs + Pages + Documents)
                   │
                   ▼
       QUESTION NORMALIZATION & TYPO TOLERANCE (Levenshtein Edit Distance)
                   │
                   ▼
     INTENT-FIRST GATEKEEPER (60+ Deterministic Regex Intent Rules)
                   │
                   ▼
     ENTITY & DEPARTMENT EXTRACTION (CSE, AIML, AI&DS, CE, ME, EE, EXTC, MBA, MCA, AS&H)
                   │
                   ▼
     MULTI-TURN SESSION CONTEXT RESOLVER (Follow-up memory across turns)
                   │
                   ▼
  RELEVANCE SCORING WITH NEGATIVE PENALTIES
  (+10 Intent, +8 Phrase, +7 Entity, +6 Category, +5 Title, +4 Heading, +3 Keyword/Synonym)
  (-10 Unrelated Category, -15 Contradictory Category, -20 Unrelated Intent)
                   │
                   ▼
  CONFIDENCE THRESHOLD CHECK (Strict Fallback on Unverified / Unknown Queries)
                   │
                   ▼
     VERIFIED RESPONSE GENERATION WITH DIRECT OFFICIAL SOURCE LINKS
```

---

## 3. Technology Stack
- **Frontend**: HTML5, Modern CSS3 (Variables, Glassmorphism, Responsive Flexbox/Grid), Vanilla JavaScript (No heavy frameworks)
- **Backend**: Python 3.10+ / 3.13, Flask 3.x
- **Database**: SQLite 3 (Pure embedded database, zero configuration)
- **Web Crawler**: `requests`, `beautifulsoup4`, `urllib.parse`
- **Document Text Extraction**: `pypdf`, `PyPDF2`
- **Security**: Password hashing via `werkzeug.security` (PBKDF2/SHA-256), Parameterized SQL queries, Session authentication

---

## 4. Folder Structure
```
PRPCEM-Chatbot/
│
├── app.py                      # Flask Application entry point and REST API
├── config.py                   # Official PRPCEM settings, limits, whitelists
├── requirements.txt            # Lightweight, free dependencies
├── README.md                   # Complete system documentation
├── test_chatbot.py             # Automated unit test suite
│
├── crawler/                    # Web Crawler Engine
│   ├── crawler.py              # Threaded crawler with change-detection & queue
│   ├── scraper.py              # HTML & Angular SPA scraper
│   ├── pdf_parser.py           # PyPDF2/pypdf safe text extraction
│   ├── text_cleaner.py         # Boilerplate stripper and content hashing
│   └── url_manager.py          # URL normalizer & domain whitelist validator
│
├── chatbot/                    # Rule-Based Conversational Engine
│   ├── chatbot_engine.py       # Main conversation coordinator & session context
│   ├── intent_rules.py         # 40+ deterministic intent regex patterns
│   ├── keyword_matcher.py      # Entity extractors (branch, round, category, year)
│   ├── synonym.py              # Rich synonym mapping dictionaries
│   ├── relevance.py            # Levenshtein distance typo tolerance & scoring
│   └── response_generator.py   # Templates for cutoff cards & verified badges
│
├── database/                   # SQLite Storage Layer
│   ├── database.py             # Connection manager, seeding & CRUD functions
│   ├── schema.sql              # 7 SQL tables and search indexes
│   └── chatbot.db              # SQLite Database file
│
├── templates/                  # Frontend HTML Templates
│   ├── index.html              # Main Standalone Chatbot UI
│   ├── admin_login.html        # Secure Admin Login
│   ├── admin.html              # Admin Control Dashboard
│   ├── history.html            # Standalone Conversation History
│   └── widget_snippet.html     # Website Floating Widget Code
│
├── static/                     # Assets
│   ├── css/
│   │   └── style.css           # 5 modern themes, glassmorphism, cutoff cards
│   ├── js/
│   │   ├── chatbot.js          # Chat controller, cards, markdown parser
│   │   ├── history.js          # Slide-out history drawer & date grouping
│   │   └── theme.js            # Theme switcher with localStorage persistence
│   └── images/
│       └── logo.svg            # PRPCEM official shield emblem
│
└── data/
    └── crawled_pages.json      # Backup summary of crawled website data
```

---

## 5. Quick Installation & Running

### Prerequisites
- Python 3.10 or newer

### Steps
1. **Navigate to the project root:**
   ```powershell
   cd c:\Users\Asus\OneDrive\Desktop\Ashu\PRPCEM-Chatbot
   ```

2. **Install required packages:**
   ```powershell
   python -m pip install -r requirements.txt
   ```

3. **Start the application:**
   ```powershell
   python app.py
   ```

4. **Open in browser:**
   ```
   http://127.0.0.1:5000
   ```

---

## 6. Features Breakdown

### A. Dedicated Cutoff System (Requirements #13 – #21)
- **Year-wise, Category-wise, and CAP Round-wise Storage**: Cutoffs are stored with `academic_year`, `course`, `branch`, `category`, `quota`, `cap_round`, `cutoff_type`, `cutoff_value`, `source_url`, and `source_date`.
- **Supported Categories**: `OPEN`, `OBC`, `SC`, `ST`, `EWS`, `TFWS`, `VJ`, `NT-B`, `NT-C`, `NT-D`, `SEBC`.
- **Supported CAP Rounds**: CAP Round 1, CAP Round 2, CAP Round 3, Spot Round.
- **Cutoff Types**: Clearly denotes `Percentile`, `Closing Rank`, or `Merit Score`. Never confuses rank with percentile.
- **Cutoff Card UI**: Renders modern glassmorphic cards showing Academic Year, Category, Round, Type, Closing Score, and an official **[View Source]** button.
- **Mandatory Disclaimer**: Displayed with every cutoff response:
  > *"Cutoffs may vary by admission year, CAP round, category, quota, seat availability and admission rules. Please verify the latest official information before making admission decisions."*

### B. College Timing Segregation (Requirements #11 & #12)
- **PRPCEM College Timing**: Strictly **10:30 AM to 5:50 PM** (Verified).
- **Segregated Timings**:
  - Library: `8:30 AM to 6:00 PM`
  - Administrative Office: `10:00 AM to 5:30 PM` (Mon-Sat, 2nd & 4th Sat off)
  - Examination Office: `10:30 AM to 5:00 PM`
  - Admission Cell: `10:00 AM to 5:00 PM`

### C. Levenshtein Typo Tolerance (Requirement #26)
Automatically corrects common student typos without Machine Learning:
- `collage` ➔ `college`
- `admisson` ➔ `admission`
- `placment` ➔ `placement`
- `departmant` ➔ `department`
- `examinaton` ➔ `examination`
- `cutof` ➔ `cutoff`
- `timng` ➔ `timing`

### D. 5 Built-in Modern Themes (Requirements #37 & #38)
Switch themes instantly with real-time UI transition. The selection is automatically saved in `localStorage`:
1. **Dark Modern (Default)**: Deep obsidian/slate background with vibrant cyan/blue accents and glow effects.
2. **Light Professional**: Crisp white/slate with deep sapphire accents.
3. **Blue College**: Academic navy with electric cyan highlights.
4. **Purple Modern**: Rich violet and indigo with neon purple accents.
5. **Green Academic**: Emerald forest tones with clean academic contrast.

### E. Chat History, New Chat, & Clear Chat (Requirements #33 – #36)
- **Top-Right Three-Dot Menu (⋮)**:
  - **🗑 Clear Chat**: Opens a confirmation dialog and clears only the active view while preserving the conversation in the database.
  - **+ New Chat**: Generates a fresh session ID, displays the welcome screen with quick chips, and saves earlier interactions to History.
  - **🕘 History**: Opens a sleek slide-out drawer grouping conversations into **Today**, **Yesterday**, and **Older**. Click any previous conversation to reload it into the chat feed.

### F. Official Web Crawler & PDF Extractor (Requirements #7 – #9)
- **Domain Restricted**: Only crawls `prpotepatilengg.ac.in`. Arbitrary external URLs are rejected.
- **Angular SPA Aware**: Inspects Angular bundles (`main.*.js`) to discover client-side routing endpoints and document URLs.
- **PDF Extraction**: Downloads official PDF circulars and extracts clean text using `pypdf`/`PyPDF2`. If a PDF is a scanned image, it records the official document link without inventing details.
- **Change Detection**: Computes SHA-256 content hashes to only update modified pages during scheduled crawls.

---

## 7. Admin Portal (`/admin`)
Access the administrative dashboard at:
```
http://127.0.0.1:5000/admin
```
- **Default Username**: `admin`
- **Default Password**: `adminpassword123`

### Admin Capabilities:
1. **Dashboard Overview**: Real-time counters for Pages, PDFs, Knowledge entries, Cutoff records, and Interactions.
2. **Web Crawler Center**:
   - `[Start Crawl]`: Initiates full background crawl.
   - `[Update Website Data]`: Refreshes content with SHA-256 change detection.
   - Live status indicator: `Crawling... Pages scanned: X, Pages stored: Y, PDFs found: Z, Errors: E`.
3. **College Information & Timing**:
   - Manage College Timing (`10:30 AM to 5:50 PM`), Office Timing, Library Timing, Exam Office Timing, Admission Helpdesk, Phone numbers, and Campus Address.
4. **Cutoffs Management**:
   - Add, Edit, Search, and Delete cutoff records with year, round, category, branch, and score.
5. **Verified Knowledge Base**:
   - Add, Edit, and Delete verified FAQs. Mark entries as verified.
6. **Crawled Pages & PDFs Viewer**:
   - Inspect all crawled pages, titles, categories, and PDF document links.

---

## 8. Official College Website Integration
The assistant is designed as a separate standalone application that seamlessly connects to the official PRPCEM website.

### Option 1: Floating Button (Bottom-Right)
Paste this snippet before `</body>` in the college website HTML:
```html
<!-- PRPCEM Assistant Floating Widget Button -->
<div id="prpcem-assistant-btn-container" style="position: fixed; bottom: 25px; right: 25px; z-index: 999999;">
  <a href="http://127.0.0.1:5000" 
     target="_blank" 
     rel="noopener"
     style="display: flex; align-items: center; gap: 10px; background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%); color: #ffffff; padding: 12px 20px; border-radius: 50px; text-decoration: none; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 15px; font-weight: 600; box-shadow: 0 8px 24px rgba(2, 132, 199, 0.4); transition: transform 0.2s ease, box-shadow 0.2s ease;"
     onmouseover="this.style.transform='scale(1.05)'"
     onmouseout="this.style.transform='scale(1)'">
    <span style="font-size: 20px;">💬</span>
    <span>Ask PRPCEM Assistant</span>
  </a>
</div>
```

### Option 2: Navigation Bar Link
Add to the main navigation menu:
```html
<a href="http://127.0.0.1:5000" target="_blank" class="btn-assistant">
  🎓 Ask PRPCEM Assistant
</a>
```

You can also view this code live at `http://127.0.0.1:5000/widget`.

---

## 9. Automated Testing
Run the comprehensive test suite verifying all 10 modules:
```powershell
python test_chatbot.py
```

### Verified Test Cases:
- `test_01_database_and_college_timing`: Verified timing `10:30 AM to 5:50 PM`.
- `test_02_college_timing_queries`: Start time, end time, hours, timing.
- `test_03_timing_segregation`: Library & office timings segregated from college hours.
- `test_04_cutoff_queries`: Year, branch, CAP round, category, and disclaimers.
- `test_05_typo_tolerance`: Levenshtein distance on misspellings.
- `test_06_no_hallucination_unknown_queries`: Zero hallucination on Mars / FIFA / irrelevant queries.
- `test_07_demo_questions`: Admissions, Courses, Fees, Placements, Hostels, Contact, Location.
- `test_08_follow_up_context`: Session branch memory across follow-ups.
- `test_09_api_endpoints`: REST API and history retrieval.
- `test_10_crawler_url_manager`: Approved domain checks & URL normalization.

---

## 10. License & Credits
Built for **P. R. Pote Patil College of Engineering & Management, Amravati**.  
Engineered with 100% free, open-source traditional programming (Zero ML / No Paid APIs).

##
