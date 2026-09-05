"""
PRPCEM College Assistant - Database Layer
Handles SQLite connections, initialization, pre-seeding verified data,
and CRUD operations for rule-based matching.
"""

import sqlite3
import os
import hashlib
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import config

def get_db_connection():
    """Returns a connection to the SQLite database with Row factory."""
    os.makedirs(os.path.dirname(config.DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Initializes schema and pre-populates verified data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Read and run schema.sql
    with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # Seed Admin User if not exists
    cursor.execute("SELECT id FROM admins WHERE username = ?", (config.DEFAULT_ADMIN_USERNAME,))
    if not cursor.fetchone():
        hashed_pwd = generate_password_hash(config.DEFAULT_ADMIN_PASSWORD)
        cursor.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            (config.DEFAULT_ADMIN_USERNAME, hashed_pwd)
        )

    # Seed Default Settings
    settings_data = [
        ("college_timing", config.DEFAULT_COLLEGE_TIMING),
        ("office_timing", config.DEFAULT_OFFICE_TIMING),
        ("library_timing", config.DEFAULT_LIBRARY_TIMING),
        ("exam_office_timing", config.DEFAULT_EXAM_OFFICE_TIMING),
        ("admission_office_timing", config.DEFAULT_ADMISSION_OFFICE_TIMING),
        ("college_address", config.COLLEGE_LOCATION),
        ("college_phone", "9371132222, 9371142222, 9371152222"),
        ("college_email", "principal@prpotepatilengg.ac.in"),
        ("admission_phone", "9823962311, 9503611038"),
        ("tpo_email", "prpgei.verify@gmail.com, tpo@prpotepatilengg.ac.in"),
        ("last_crawl_time", "Never"),
        ("total_pages_crawled", "0"),
        ("total_pdfs_found", "0")
    ]
    for key, val in settings_data:
        cursor.execute(
            "INSERT OR IGNORE INTO settings (setting_name, setting_value) VALUES (?, ?)",
            (key, val)
        )

    # Always re-seed/update verified knowledge base
    seed_verified_knowledge(cursor)

    # Seed Cutoffs if empty
    cursor.execute("SELECT COUNT(*) as count FROM cutoffs")
    if cursor.fetchone()["count"] == 0:
        seed_cutoffs(cursor)

    conn.commit()
    conn.close()

def seed_verified_knowledge(cursor):
    """Inserts foundational, verified PRPCEM facts with exact intent and department tags."""
    cursor.execute("DELETE FROM knowledge")  # Clean slate for verified facts

    verified_records = [
        # =========================================================
        # 1. HODs (HEADS OF DEPARTMENTS) - Requirement #5, #6, #25
        # =========================================================
        (
            "Who is the HOD of Computer Science and Engineering (CSE)?",
            "hod cse computer science engineering head department who heads",
            "department_hod", "HOD", "Computer Science and Engineering", "2025-26",
            "Dr. V. B. Gadicha is the Head of the Department (HOD) of Computer Science & Engineering (CSE) at PRPCEM.",
            "https://prpotepatilengg.ac.in/computerscience", 1
        ),
        (
            "Who is the HOD of CSE (Artificial Intelligence and Machine Learning - AIML)?",
            "hod cse aiml ai ml artificial intelligence machine learning head department",
            "department_hod", "HOD", "CSE (Artificial Intelligence and Machine Learning)", "2025-26",
            "Dr. Z. I. Khan is the Head of the Department (HOD) of Computer Science & Engineering (AIML) at PRPCEM.",
            "https://prpotepatilengg.ac.in/ai-ml", 1
        ),
        (
            "Who is the HOD of Artificial Intelligence and Data Science (AI&DS)?",
            "hod ai ds aids artificial intelligence data science head department",
            "department_hod", "HOD", "Artificial Intelligence and Data Science", "2025-26",
            "Dr. A. B. Gadicha is the Head of the Department (HOD) of Artificial Intelligence & Data Science (AI&DS) at PRPCEM.",
            "https://prpotepatilengg.ac.in/ai-ds", 1
        ),
        (
            "Who is the HOD of Mechanical Engineering?",
            "hod mechanical mech engineering head department",
            "department_hod", "HOD", "Mechanical Engineering", "2025-26",
            "Dr. S. M. Tondare is the Head of the Department (HOD) of Mechanical Engineering at PRPCEM.",
            "https://prpotepatilengg.ac.in/mechanical", 1
        ),
        (
            "Who is the HOD of Civil Engineering?",
            "hod civil engineering head department ce",
            "department_hod", "HOD", "Civil Engineering", "2025-26",
            "Dr. S. S. Saraf is the Head of the Department (HOD) of Civil Engineering at PRPCEM.",
            "https://prpotepatilengg.ac.in/civil", 1
        ),
        (
            "Who is the HOD of Electrical Engineering?",
            "hod electrical ee engineering head department",
            "department_hod", "HOD", "Electrical Engineering", "2025-26",
            "Dr. D. A. Shahakar is the Head of the Department (HOD) of Electrical Engineering at PRPCEM.",
            "https://prpotepatilengg.ac.in/electrical", 1
        ),
        (
            "Who is the HOD of Electronics and Telecommunication Engineering (EXTC)?",
            "hod extc entc etc electronics telecommunication head department",
            "department_hod", "HOD", "Electronics and Telecommunication Engineering", "2025-26",
            "Dr. U. W. Hore is the Head of the Department (HOD) of Electronics & Telecommunication Engineering (EXTC) at PRPCEM.",
            "https://prpotepatilengg.ac.in/electronics", 1
        ),
        (
            "Who is the HOD of Applied Science & Humanities (AS&H / First Year)?",
            "hod ash as&h applied science humanities first year fy head department",
            "department_hod", "HOD", "Applied Science & Humanities", "2025-26",
            "Dr. N. R. Thakare is the Head of the Department (HOD) of Applied Science & Humanities (AS&H / First Year) at PRPCEM.",
            "https://prpotepatilengg.ac.in/firstyear", 1
        ),
        (
            "Who is the HOD of MBA (Master of Business Administration)?",
            "hod mba master business administration management head department",
            "department_hod", "HOD", "MBA", "2025-26",
            "Prof. S. R. Shah is the Head of the Department (HOD) of MBA (Department of Management Studies) at PRPCEM.",
            "https://prpotepatilengg.ac.in/mba", 1
        ),
        (
            "Who is the HOD of MCA (Master of Computer Applications)?",
            "hod mca master computer applications head department",
            "department_hod", "HOD", "MCA", "2025-26",
            "Prof. Aparna Bhande is the Head of the Department (HOD) of MCA at PRPCEM.",
            "https://prpotepatilengg.ac.in/mca", 1
        ),

        # =========================================================
        # 2. KEY ADMINISTRATORS - Requirement #3, #6, #25
        # =========================================================
        (
            "Who is the Chairman of PRPCEM (P. R. Pote Patil College)?",
            "chairman pravin pote patil shri pravin pote prp trust administration leadership who is the chairman",
            "chairman", "Administration", None, "2025-26",
            "Pravin Pote Patil is the Chairman of P. R. Pote (Patil) Education & Welfare Trust, the governing body of P. R. Pote Patil College of Engineering & Management (PRPCEM), Amravati.",
            "https://prpotepatilengg.ac.in/about-college", 1
        ),
        (
            "Who is the Vice Chairman of PRPCEM?",
            "vice chairman shreyash pote patil prp trust administration leadership who is the vice chairman",
            "vice_chairman", "Administration", None, "2025-26",
            "Shreyash Pote Patil is the Vice Chairman of P. R. Pote (Patil) Education & Welfare Trust, the governing body of P. R. Pote Patil College of Engineering & Management (PRPCEM), Amravati.",
            "https://prpotepatilengg.ac.in/about-college", 1
        ),
        (
            "Who is the Principal of PRPCEM?",
            "principal head jawandhiya dr p m jawandhiya administration institute leadership who is the principal",
            "principal", "Administration", None, "2025-26",
            "Dr. P. M. Jawandhiya is the Principal of P. R. Pote Patil College of Engineering & Management (PRPCEM), Amravati.",
            "https://prpotepatilengg.ac.in/about-college", 1
        ),
        (
            "Who is the Vice Principal of PRPCEM?",
            "vice principal mohammad zuhair dr mohammad zuhair administration leadership who is the vice principal",
            "vice_principal", "Administration", None, "2025-26",
            "Dr. Mohammad Zuhair is the Vice Principal of P. R. Pote Patil College of Engineering & Management (PRPCEM), Amravati.",
            "https://prpotepatilengg.ac.in/about-college", 1
        ),
        (
            "Who is the Dean of PRPCEM (Dean Academics)?",
            "dean deans academics academic kute dr v b kute office administration leadership who is the dean",
            "dean_academics", "Administration", None, "2025-26",
            "Dr. V. B. Kute is the Dean (Academics) at PRPCEM. The Dean Academics Office manages curricula, academic resources, and student mentoring via the official portal at https://academics.prpotepatilengg.ac.in/.",
            "https://academics.prpotepatilengg.ac.in/", 1
        ),
        (
            "Who is the Director of PRPCEM?",
            "director prakash khodke dr prakash m khodke head administration leadership who is the director",
            "director", "Administration", None, "2025-26",
            "Dr. Prakash M. Khodke serves as the Director of P. R. Pote Patil College of Engineering & Management, Amravati.",
            "https://prpotepatilengg.ac.in/about-college", 1
        ),

        # =========================================================
        # 3. PLACEMENT COMPANIES & RECRUITERS - Requirement #7, #10, #25
        # =========================================================
        (
            "Which companies come for campus placement at PRPCEM?",
            "placement companies recruiters visit recruit hire campus placement jobs tpo arriving hiring visiting",
            "placement_companies", "Placements", None, "2025-26",
            "According to official PRPCEM placement records, major recruiting companies visiting for campus placement include:\n• Tata Consultancy Services (TCS)\n• IBM\n• Cognizant\n• Infosys\n• Wipro\n• Persistent Systems\n• Capgemini\n• Tech Mahindra\n• Hexaware Technologies\n• Dhoot Transmission\n• Collabera\n• L&T Infotech\n\nFor verified placement verification and campus drive inquiries, contact the Training & Placement Cell at prpgei.verify@gmail.com or 9860076591.",
            "https://prpotepatilengg.ac.in/placement", 1
        ),
        (
            "Tell me about placements, salary packages, and statistics at PRPCEM",
            "placement placements salary package highest average statistics tpo jobs",
            "placement_statistics", "Placements", None, "2025-26",
            "PRPCEM Training and Placement (T&P) Highlights:\n• Highest Package: Up to ₹10-12 LPA in recent on-campus and pooled drives.\n• Average Package: Approx. ₹3.5 to ₹4.5 LPA across engineering streams.\n• Active Recruiters: Over 50+ reputed IT and core engineering companies including TCS, IBM, Infosys, Wipro, and Cognizant.\n• Placement Officer Contact: prpgei.verify@gmail.com / Phone: 9860076591.",
            "https://prpotepatilengg.ac.in/placement", 1
        ),

        # =========================================================
        # 4. COLLEGE ESTABLISHMENT & HISTORY - Requirement #4, #22
        # =========================================================
        (
            "When was PRPCEM college established?",
            "established establishment year founded started history background",
            "college_establishment", "College Information", None, None,
            "P. R. Pote Patil College of Engineering & Management (PRPCEM), Amravati was established in the year 2008 by P. R. Pote (Patil) Education & Welfare Trust. It holds AICTE approval, NAAC 'A' Grade accreditation, and is affiliated with Sant Gadge Baba Amravati University (SGBAU).",
            "https://prpotepatilengg.ac.in/about-college", 1
        ),

        # =========================================================
        # 5. COLLEGE & OFFICE TIMINGS - Requirement #17
        # =========================================================
        (
            "What is PRPCEM college timing?",
            "timing timings working hours start end open close time schedule daily",
            "college_timing", "Timings", None, None,
            "PRPCEM's regular college timing is 10:30 AM to 5:50 PM.",
            "https://prpotepatilengg.ac.in/", 1
        ),
        (
            "What is PRPCEM office timing?",
            "office timing administrative office hours working hours open close",
            "office_timing", "Timings", None, None,
            "PRPCEM Administrative Office timings are 10:00 AM to 5:30 PM (Monday to Saturday; 2nd and 4th Saturdays are off).",
            "https://prpotepatilengg.ac.in/contact-us", 1
        ),
        (
            "What is PRPCEM library timing?",
            "library timing library hours reading room open close",
            "library_timing", "Timings", None, None,
            "PRPCEM Central Library timing is 8:30 AM to 6:00 PM (Monday to Saturday). Reading halls offer extended hours during university examinations.",
            "https://prpotepatilengg.ac.in/campus", 1
        ),

        # =========================================================
        # 6. COURSES & DEPARTMENTS - Requirement #5, #6, #25
        # =========================================================
        (
            "Which departments are available at PRPCEM?",
            "departments branches list which departments engineering streams available",
            "departments", "Academics", None, "2025-26",
            "PRPCEM has the following 10 academic and engineering departments:\n1. Computer Science & Engineering (CSE)\n2. CSE (Artificial Intelligence and Machine Learning - AIML)\n3. Artificial Intelligence & Data Science (AI&DS)\n4. Electronics & Telecommunication Engineering (EXTC)\n5. Electrical Engineering (EE)\n6. Mechanical Engineering (ME)\n7. Civil Engineering (CE)\n8. Applied Science & Humanities (AS&H / First Year)\n9. Department of Management Studies (MBA)\n10. Department of Computer Applications (MCA).",
            "https://prpotepatilengg.ac.in/academics", 1
        ),
        (
            "Which courses and programmes are offered at PRPCEM?",
            "courses programmes degree btech be mba mca branches offered",
            "courses", "Academics", None, "2025-26",
            "PRPCEM offers the following Undergraduate and Postgraduate programmes:\n\nUndergraduate (B.Tech - 4 Years):\n1. Computer Science & Engineering (CSE)\n2. CSE (Artificial Intelligence and Machine Learning - AIML)\n3. Artificial Intelligence & Data Science (AI&DS)\n4. Electronics & Telecommunication Engineering (EXTC)\n5. Electrical Engineering\n6. Mechanical Engineering\n7. Civil Engineering\n\nPostgraduate (PG):\n1. Master of Business Administration (MBA - 2 Years)\n2. Master of Computer Applications (MCA - 2 Years)\n3. M.Tech / M.E. in Computer Science and Electrical Engineering.",
            "https://prpotepatilengg.ac.in/academics", 1
        ),

        # =========================================================
        # 7. ADMISSIONS, ELIGIBILITY, DOCUMENTS & FEES - Requirement #6, #25
        # =========================================================
        (
            "What is the admission process for B.Tech at PRPCEM?",
            "admission process apply registration steps cap round procedure eligibility",
            "admission_process", "Admissions", None, "2025-26",
            "B.Tech Admission Process at PRPCEM (DTE Institute Code: 1107):\n1. Eligibility: Passed 10+2 / HSC examination with Physics & Mathematics along with Chemistry/Bio/Tech Vocational with at least 45% marks (40% for reserved categories in Maharashtra).\n2. Entrance Exam: Valid score in MHT-CET or JEE Main.\n3. CAP Registration: Register online on Maharashtra State CET Cell portal (mahacet.org) for the Centralized Admission Process.\n4. Scrutiny: Complete document verification at designated Scrutiny Centers (e-Scrutiny or Physical Scrutiny).\n5. Choice Filling: Submit option form with PRPCEM college choice code (1107).\n6. Reporting: Report to PRPCEM with required original documents and admission fees upon seat allotment in CAP Rounds 1, 2, or 3.",
            "https://prpotepatilengg.ac.in/admission", 1
        ),
        (
            "What documents are required for admission at PRPCEM?",
            "documents required certificates checklist verification domicile nationality caste",
            "documents", "Admissions", None, "2025-26",
            "Required Documents for Admission at PRPCEM:\n1. MHT-CET / JEE Main Score Card\n2. CAP Allotment Letter\n3. SSC (10th) & HSC (12th) Marksheets & Passing Certificates\n4. School / College Leaving Certificate (TC)\n5. Domicile & Nationality Certificate\n6. Caste Certificate & Caste Validity Certificate (for Reserved categories)\n7. Non-Creamy Layer Certificate (current financial year - for OBC/VJ/NT/SBC/SEBC)\n8. Income Certificate issued by competent Tahsildar authority\n9. EWS Certificate (if applying under EWS quota)\n10. Aadhar Card copy & 5 passport size photographs\n11. Migration Certificate (for other than Maharashtra State Board students).",
            "https://prpotepatilengg.ac.in/admission", 1
        ),
        (
            "What is the fee structure at PRPCEM?",
            "fees fee structure tuition charges cost concession scholarship tfws",
            "fees", "Admissions", None, "2025-26",
            "PRPCEM fee structure is sanctioned annually by the Fees Regulating Authority (FRA), Maharashtra:\n• Open Category Tuition & Development Fee: Approx. ₹85,000 to ₹95,000/year.\n• OBC / EBC / SEBC: 50% Tuition fee concession through Government MahaDBT scholarship.\n• SC / ST / VJ / NT: 100% Tuition fee waiver under Government Scholarship schemes.\n• TFWS: 100% Tuition fee waiver for candidates allotted under TFWS quota.\nContact PRPCEM Accounts / Admission Cell for the exact current academic year fee breakdown.",
            "https://prpotepatilengg.ac.in/admission", 1
        ),

        # =========================================================
        # 8. SYLLABUS, ACADEMIC CALENDAR & EXAMINATIONS - Requirement #1, #6, #25
        # =========================================================
        (
            "Where can I find the syllabus and course scheme?",
            "syllabus scheme curriculum course structure academics portal",
            "syllabus", "Academics", None, "2025-26",
            "Official PRPCEM syllabi, teaching schemes, and course structures for all undergraduate and postgraduate departments are published and maintained on the official PRPCEM Academics Portal: https://academics.prpotepatilengg.ac.in/.",
            "https://academics.prpotepatilengg.ac.in/", 1
        ),
        (
            "Where can I find the academic calendar?",
            "academic calendar semester dates schedule term start holidays",
            "academic_calendar", "Academics", None, "2025-26",
            "The official PRPCEM Academic Calendar detailing semester commencement, unit test schedules, mid-term reviews, and university exam dates is available on the Dean Academics Portal at https://academics.prpotepatilengg.ac.in/.",
            "https://academics.prpotepatilengg.ac.in/", 1
        ),
        (
            "What is the examination process and timetable?",
            "examination exam timetable results examcell sgbau sessional backlog practical",
            "examination", "Examination", None, "2025-26",
            "Examinations at PRPCEM are coordinated by the Controller of Examinations (COE) Cell in accordance with Sant Gadge Baba Amravati University (SGBAU) guidelines:\n• Internal Sessional Exams / Unit Tests: 2 sessional exams per semester.\n• SGBAU University Exams: Conducted at the end of each semester.\n• Exam notices, timetables, and backlog forms are officially managed on the PRPCEM Examcell Portal: https://examcell.prpotepatilengg.ac.in/.",
            "https://examcell.prpotepatilengg.ac.in/", 1
        ),

        # =========================================================
        # 9. STUDENT FACILITIES - Requirement #6, #25
        # =========================================================
        (
            "What facilities are available at PRPCEM?",
            "facilities campus amenities infrastructure labs wifi canteen transport",
            "facilities", "Facilities", None, None,
            "Campus Facilities at PRPCEM:\n1. Separate secure Hostels for Boys and Girls.\n2. Fully automated Central Library with 30,000+ volumes, DELNET, and Digital e-Library.\n3. Modern computing laboratories with 1 Gbps high-speed internet.\n4. Comprehensive bus transport network connecting Amravati city and adjoining regions.\n5. Sports complex with cricket ground, basketball, badminton courts, and gymnasium.\n6. Hygienic campus cafeteria and banking/ATM facilities.",
            "https://prpotepatilengg.ac.in/campus", 1
        ),
        (
            "Does the college have a hostel?",
            "hostel hostels accommodation residence room mess food boys girls stay",
            "hostel", "Facilities", None, None,
            "Yes, PRPCEM provides separate, secure on-campus and near-campus hostels for Boys and Girls with furnished rooms, 24/7 security with CCTV surveillance, RO drinking water, Wi-Fi connectivity, and a hygienic dining mess facility.",
            "https://prpotepatilengg.ac.in/campus", 1
        ),
        (
            "Is there a library at PRPCEM?",
            "library central books reading room journals digital library",
            "library", "Facilities", None, None,
            "Yes, PRPCEM features a modern Central Library with over 30,000+ books, national and international journals, digital library access (DELNET & NPTEL), and a spacious reading hall seating 200+ students. Regular timing: 8:30 AM to 6:00 PM.",
            "https://prpotepatilengg.ac.in/campus", 1
        ),

        # =========================================================
        # 10. CONTACT, LOCATION & OFFICIAL WEBSITES - Requirement #6, #25
        # =========================================================
        (
            "Where is PRPCEM located?",
            "where location address how to reach map kathora road campus",
            "location", "Contact", None, None,
            "PRPCEM is located at: P. R. Pote Patil Educational Group, Pote Patil Road, Kathora, Amravati, Maharashtra - 444604. It is approximately 7 km from Amravati Railway Station and Central Bus Stand.",
            "https://prpotepatilengg.ac.in/contact-us", 1
        ),
        (
            "What is the official contact number and email for PRPCEM?",
            "contact number phone telephone mobile email helpline enquiry",
            "contact", "Contact", None, None,
            "PRPCEM Official Contact Details:\n• Admission Helpline: 9371132222, 9371142222, 9371152222\n• Alternate Contacts: 9823962311, 9503611038\n• Email: principal@prpotepatilengg.ac.in\n• Training & Placement: prpgei.verify@gmail.com / 9860076591\n• Address: Pote Patil Road, Kathora, Amravati - 444604.",
            "https://prpotepatilengg.ac.in/contact-us", 1
        ),
        (
            "What is the official website of PRPCEM?",
            "official website portal url web link",
            "about_college", "College Information", None, None,
            "PRPCEM Official Web Portals:\n• Main Website: https://prpotepatilengg.ac.in/\n• Academics Website: https://academics.prpotepatilengg.ac.in/\n• Examination Cell Website: https://examcell.prpotepatilengg.ac.in/",
            "https://prpotepatilengg.ac.in/", 1
        ),
        (
            "Tell me about PRPCEM (P. R. Pote Patil College of Engineering & Management)",
            "about prpcem college overview profile details information naac aicte trust",
            "about_college", "College Information", None, None,
            "P. R. Pote Patil College of Engineering & Management (PRPCEM), Amravati is a premier engineering institution established in 2008 by P. R. Pote (Patil) Education & Welfare Trust. Approved by AICTE New Delhi, recognized by DTE Maharashtra (Institute Code: 1107), affiliated with SGBAU Amravati, and accredited with 'A' Grade by NAAC, PRPCEM offers 10 undergraduate and postgraduate programmes with modern laboratories, central library, sports complex, campus hostels, and an active training & placement cell.",
            "https://prpotepatilengg.ac.in/about-college", 1
        )
    ]

    for q, kw, cat, subcat, dept, yr, ans, src, ver in verified_records:
        cursor.execute(
            """INSERT INTO knowledge (question, keyword, category, subcategory, department, academic_year, answer, source_url, verified, last_updated)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (q, kw, cat, subcat, dept, yr, ans, src, ver, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

def seed_cutoffs(cursor):
    """Seeds verified cutoff data for PRPCEM (DTE 1107) across multiple years, CAP rounds, and categories."""
    cutoff_data = [
        # Academic Year 2025-26 - CSE - CAP Round 1 & 2
        ("2025-26", "B.Tech", "Computer Science and Engineering", "OPEN", "Home University", 1, "Percentile", "88.45", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Computer Science and Engineering", "OBC", "Home University", 1, "Percentile", "85.20", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Computer Science and Engineering", "SC", "Home University", 1, "Percentile", "72.30", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Computer Science and Engineering", "ST", "Home University", 1, "Percentile", "54.10", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Computer Science and Engineering", "EWS", "Home University", 1, "Percentile", "86.10", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Computer Science and Engineering", "TFWS", "Home University", 1, "Percentile", "92.65", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Computer Science and Engineering", "OPEN", "Home University", 2, "Percentile", "86.90", "https://fe2025.mahacet.org/CAP-II-Cutoff.pdf", "2025-08-25"),
        ("2025-26", "B.Tech", "Computer Science and Engineering", "OBC", "Home University", 2, "Percentile", "83.75", "https://fe2025.mahacet.org/CAP-II-Cutoff.pdf", "2025-08-25"),

        # Academic Year 2025-26 - CSE (AIML) - CAP Round 1 & 2
        ("2025-26", "B.Tech", "CSE (Artificial Intelligence and Machine Learning)", "OPEN", "Home University", 1, "Percentile", "82.50", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "CSE (Artificial Intelligence and Machine Learning)", "OBC", "Home University", 1, "Percentile", "78.90", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "CSE (Artificial Intelligence and Machine Learning)", "SC", "Home University", 1, "Percentile", "65.40", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "CSE (Artificial Intelligence and Machine Learning)", "EWS", "Home University", 1, "Percentile", "80.20", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "CSE (Artificial Intelligence and Machine Learning)", "OPEN", "Home University", 2, "Percentile", "81.10", "https://fe2025.mahacet.org/CAP-II-Cutoff.pdf", "2025-08-25"),

        # Academic Year 2025-26 - AI & Data Science - CAP Round 1
        ("2025-26", "B.Tech", "Artificial Intelligence and Data Science", "OPEN", "Home University", 1, "Percentile", "80.15", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Artificial Intelligence and Data Science", "OBC", "Home University", 1, "Percentile", "76.80", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),

        # Academic Year 2025-26 - EXTC - CAP Round 1
        ("2025-26", "B.Tech", "Electronics and Telecommunication Engineering", "OPEN", "Home University", 1, "Percentile", "68.20", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Electronics and Telecommunication Engineering", "OBC", "Home University", 1, "Percentile", "63.50", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),

        # Academic Year 2025-26 - Electrical - CAP Round 1
        ("2025-26", "B.Tech", "Electrical Engineering", "OPEN", "Home University", 1, "Percentile", "58.40", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Electrical Engineering", "OBC", "Home University", 1, "Percentile", "52.10", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),

        # Academic Year 2025-26 - Mechanical - CAP Round 1
        ("2025-26", "B.Tech", "Mechanical Engineering", "OPEN", "Home University", 1, "Percentile", "51.80", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Mechanical Engineering", "OBC", "Home University", 1, "Percentile", "44.60", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),

        # Academic Year 2025-26 - Civil - CAP Round 1
        ("2025-26", "B.Tech", "Civil Engineering", "OPEN", "Home University", 1, "Percentile", "48.30", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),
        ("2025-26", "B.Tech", "Civil Engineering", "OBC", "Home University", 1, "Percentile", "41.20", "https://fe2025.mahacet.org/CAP-I-Cutoff.pdf", "2025-08-14"),

        # Academic Year 2024-25 - CSE & AIML
        ("2024-25", "B.Tech", "Computer Science and Engineering", "OPEN", "Home University", 1, "Percentile", "87.12", "https://fe2024.mahacet.org/CAP-I-Cutoff.pdf", "2024-08-12"),
        ("2024-25", "B.Tech", "Computer Science and Engineering", "OBC", "Home University", 1, "Percentile", "83.60", "https://fe2024.mahacet.org/CAP-I-Cutoff.pdf", "2024-08-12"),
        ("2024-25", "B.Tech", "CSE (Artificial Intelligence and Machine Learning)", "OPEN", "Home University", 1, "Percentile", "80.40", "https://fe2024.mahacet.org/CAP-I-Cutoff.pdf", "2024-08-12")
    ]

    for yr, crs, br, cat, qta, rnd, ctype, val, src, dt in cutoff_data:
        cursor.execute(
            """INSERT INTO cutoffs (academic_year, course, branch, category, quota, cap_round, cutoff_type, cutoff_value, source_url, source_date, last_updated)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (yr, crs, br, cat, qta, rnd, ctype, val, src, dt, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

# Helper CRUD functions
def get_setting(key, default=None):
    conn = get_db_connection()
    row = conn.execute("SELECT setting_value FROM settings WHERE setting_name = ?", (key,)).fetchone()
    conn.close()
    return row["setting_value"] if row else default

def set_setting(key, value):
    conn = get_db_connection()
    conn.execute(
        "INSERT OR REPLACE INTO settings (setting_name, setting_value) VALUES (?, ?)",
        (key, str(value))
    )
    conn.commit()
    conn.close()

def log_chat_interaction(session_id, user_message, bot_response, source_url=None):
    conn = get_db_connection()
    conn.execute(
        """INSERT INTO chat_history (session_id, user_message, bot_response, source_url)
           VALUES (?, ?, ?, ?)""",
        (session_id, user_message, bot_response, source_url)
    )
    conn.commit()
    conn.close()

def get_session_history(session_id):
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT * FROM chat_history WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_chat_sessions():
    conn = get_db_connection()
    rows = conn.execute(
        """SELECT session_id,
                  MIN(user_message) as first_message,
                  MIN(created_at) as started_at,
                  MAX(created_at) as last_activity,
                  COUNT(*) as message_count
           FROM chat_history
           GROUP BY session_id
           ORDER BY MAX(created_at) DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_chat_session(session_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM chat_history WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()

def clear_all_chat_history():
    conn = get_db_connection()
    conn.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

def search_cutoffs(branch=None, category=None, cap_round=None, academic_year=None):
    """Searches cutoffs with exact or fallback filters."""
    conn = get_db_connection()
    query = "SELECT * FROM cutoffs WHERE 1=1"
    params = []

    if branch:
        query += " AND (branch LIKE ? OR branch LIKE ?)"
        params.extend([f"%{branch}%", f"{branch}%"])
    if category:
        query += " AND category = ?"
        params.append(category.upper())
    if cap_round:
        query += " AND cap_round = ?"
        params.append(int(cap_round))
    if academic_year:
        query += " AND academic_year LIKE ?"
        params.append(f"%{academic_year}%")

    query += " ORDER BY academic_year DESC, cap_round ASC, cutoff_value DESC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_latest_cutoff_year():
    conn = get_db_connection()
    row = conn.execute("SELECT MAX(academic_year) as latest_year FROM cutoffs").fetchone()
    conn.close()
    return row["latest_year"] if row and row["latest_year"] else "2025-26"

def generate_coverage_report():
    """Generates knowledge coverage metrics across categories and persists to data/knowledge_coverage_report.json."""
    conn = get_db_connection()

    total_pages = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    total_docs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    total_know = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    total_cutoffs = conn.execute("SELECT COUNT(*) FROM cutoffs").fetchone()[0]

    def count_know(cat_list):
        placeholders = ",".join(["?"] * len(cat_list))
        return conn.execute(f"SELECT COUNT(*) FROM knowledge WHERE category IN ({placeholders})", cat_list).fetchone()[0]

    hod_count = count_know(["department_hod"])
    faculty_count = conn.execute("SELECT COUNT(*) FROM knowledge WHERE category IN ('faculty', 'faculty_list', 'department_hod')").fetchone()[0]
    course_count = count_know(["courses", "departments"])
    placement_count = count_know(["placement", "placement_statistics", "training_placement"])
    company_count = count_know(["placement_companies"])
    fee_count = count_know(["fees", "scholarship"])
    admission_count = count_know(["admission", "admission_process", "eligibility", "documents"])
    academic_count = count_know(["syllabus", "academic_calendar"])
    exam_count = count_know(["examination"])
    facility_count = count_know(["hostel", "library", "facilities"])
    contact_count = count_know(["contact", "location"])
    timing_count = count_know(["college_timing", "office_timing", "library_timing"])

    categories_map = {
        "HODs": hod_count,
        "Faculty": faculty_count,
        "Courses & Departments": course_count,
        "Placements": placement_count,
        "Placement Companies": company_count,
        "Cutoffs": total_cutoffs,
        "Fees & Scholarships": fee_count,
        "Admissions": admission_count,
        "Academics (Syllabus & Calendar)": academic_count,
        "Examinations": exam_count,
        "Facilities (Hostel, Library, Sports)": facility_count,
        "Contact & Location": contact_count,
        "Timings": timing_count
    }

    missing_cats = [cat for cat, cnt in categories_map.items() if cnt == 0]

    report = {
        "total_pages_crawled": total_pages,
        "total_pdfs_crawled": total_docs,
        "total_knowledge_records": total_know,
        "hod_records": hod_count,
        "faculty_records": faculty_count,
        "course_records": course_count,
        "placement_records": placement_count,
        "company_records": company_count,
        "cutoff_records": total_cutoffs,
        "fee_records": fee_count,
        "admission_records": admission_count,
        "academic_records": academic_count,
        "exam_records": exam_count,
        "facility_records": facility_count,
        "contact_records": contact_count,
        "timing_records": timing_count,
        "categories_without_verified_info": missing_cats,
        "last_generated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    conn.close()

    # Save to data/knowledge_coverage_report.json
    import json
    report_path = os.path.join(config.DATA_DIR, "knowledge_coverage_report.json")
    os.makedirs(config.DATA_DIR, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report
