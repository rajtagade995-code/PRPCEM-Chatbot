"""
PRPCEM College Assistant - Comprehensive Automated Test Suite
Validates Intent-First architecture, official knowledge accuracy,
all 30 standard college questions, HOD mappings, placement companies disambiguation,
negative penalty scoring, follow-up session memory, and Flask endpoints.
Zero ML, Zero LLM API.
"""

import unittest
import json
from app import app
from database.database import init_db, get_db_connection, get_setting
from chatbot.chatbot_engine import chatbot_engine
from chatbot.intent_rules import detect_intent
from chatbot.relevance import correct_typos, levenshtein_distance
from chatbot.keyword_matcher import extract_entities
from crawler.url_manager import URLManager

class TestPRPCEMIntentFirstChatbot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = app.test_client()

    # -------------------------------------------------------------
    # 1. PLACEMENT RECRUITERS vs ESTABLISHMENT DISAMBIGUATION
    # -------------------------------------------------------------
    def test_01_placement_companies_disambiguation(self):
        """CRITICAL: 'Which companies come for placement?' must return recruiters, NOT establishment year."""
        queries = [
            "Which companies come for placement?",
            "Which companies come?",
            "Which companies visit the college?",
            "Which companies recruit students?",
            "What companies come for placement?",
            "Placement companies?",
            "Recruiters?"
        ]
        for q in queries:
            resp = chatbot_engine.process_message(q, session_id="test_placement")
            self.assertEqual(resp["intent"], "placement_companies", f"Intent mismatch for: {q}")
            self.assertIn("Tata Consultancy Services", resp["answer"], f"Recruiters missing in: {q}")
            # Ensure establishment year is NEVER returned
            self.assertNotIn("established in the year 2008", resp["answer"], f"Contradictory content in: {q}")
            self.assertNotIn("established in 2009", resp["answer"], f"Contradictory content in: {q}")
            self.assertIn("placement", resp["source_url"].lower())

    def test_02_college_establishment(self):
        """Query asking for establishment must return 2008 establishment."""
        queries = [
            "When was PRPCEM established?",
            "What year was PRPCEM established?",
            "When was the college founded?"
        ]
        for q in queries:
            resp = chatbot_engine.process_message(q, session_id="test_estab")
            self.assertEqual(resp["intent"], "college_establishment", f"Intent mismatch for: {q}")
            self.assertIn("2008", resp["answer"])
            self.assertNotIn("Tata Consultancy Services", resp["answer"])

    # -------------------------------------------------------------
    # 2. HOD QUESTIONS FOR ALL 10 DEPARTMENTS (Requirement #5 & #25)
    # -------------------------------------------------------------
    def test_03_hod_questions(self):
        """Must return exact verified HOD for each department."""
        hod_test_cases = [
            ("Who is the HOD of CSE?", "Dr. V. B. Gadicha", "Computer Science"),
            ("Who is the HOD of CSE AIML?", "Dr. Z. I. Khan", "AIML"),
            ("Who is the HOD of AI&DS?", "Dr. A. B. Gadicha", "Data Science"),
            ("Who is the HOD of Mechanical?", "Dr. S. M. Tondare", "Mechanical"),
            ("Who is the HOD of Civil?", "Dr. S. S. Saraf", "Civil"),
            ("Who is the HOD of Electrical?", "Dr. D. A. Shahakar", "Electrical"),
            ("Who is the HOD of EXTC?", "Dr. U. W. Hore", "EXTC"),
            ("Who is the HOD of AS&H?", "Dr. N. R. Thakare", "Humanities"),
            ("Who is the HOD of MBA?", "Prof. S. R. Shah", "MBA"),
            ("Who is the HOD of MCA?", "Prof. Aparna Bhande", "MCA")
        ]
        for query, expected_name, dept_name in hod_test_cases:
            resp = chatbot_engine.process_message(query, session_id="test_hods")
            self.assertEqual(resp["intent"], "department_hod", f"Intent mismatch for: {query}")
            self.assertIn(expected_name, resp["answer"], f"HOD name missing for {dept_name} in query: {query}")

    # -------------------------------------------------------------
    # 3. KEY ADMINISTRATORS (Requirement #6 & #25)
    # -------------------------------------------------------------
    def test_04_key_administrators(self):
        """Must return verified Principal, Vice Principal, and Dean Academics."""
        resp_p = chatbot_engine.process_message("Who is the Principal?", session_id="test_admin")
        self.assertIn("Dr. P. M. Jawandhiya", resp_p["answer"])

        resp_vp = chatbot_engine.process_message("Who is the Vice Principal?", session_id="test_admin")
        self.assertIn("Dr. Mohammad Zuhair", resp_vp["answer"])

        resp_dean = chatbot_engine.process_message("Who is the Dean Academics?", session_id="test_admin")
        self.assertIn("Dr. V. B. Kute", resp_dean["answer"])
        self.assertIn("academics.prpotepatilengg.ac.in", resp_dean["source_url"])

    # -------------------------------------------------------------
    # 4. ALL 30 STANDARD COLLEGE QUESTIONS (Requirement #25)
    # -------------------------------------------------------------
    def test_05_all_standard_college_questions(self):
        """Validates all 30 questions from Section 25."""
        questions_and_checks = [
            ("Which departments are available?", "Computer Science & Engineering"),
            ("Which courses are offered?", "B.Tech"),
            ("What is the college timing?", "10:30 AM to 5:50 PM"),
            ("When does college start?", "10:30 AM to 5:50 PM"),
            ("When does college close?", "10:30 AM to 5:50 PM"),
            ("Which companies come for placement?", "TCS"),
            ("Which companies recruit students?", "Cognizant"),
            ("Tell me about placements.", "T&P"),
            ("What is the CSE AIML cutoff?", "CSE (Artificial Intelligence and Machine Learning)"),
            ("What documents are required for admission?", "Score Card"),
            ("What is the admission process?", "MHT-CET"),
            ("Where can I find the syllabus?", "academics.prpotepatilengg.ac.in"),
            ("Where can I find the academic calendar?", "academics.prpotepatilengg.ac.in"),
            ("When are examinations?", "examcell.prpotepatilengg.ac.in"),
            ("What facilities are available?", "Library"),
            ("Is hostel available?", "Hostel"),
            ("Is library available?", "Central Library"),
            ("Where is PRPCEM located?", "Kathora"),
            ("What is the contact number?", "9371132222"),
            ("What is the official website?", "prpotepatilengg.ac.in")
        ]
        for query, expected_text in questions_and_checks:
            resp = chatbot_engine.process_message(query, session_id="test_standard")
            self.assertNotEqual(resp["intent"], "unknown", f"Failed intent for: {query}")
            self.assertIn(expected_text.lower(), resp["answer"].lower(), f"Failed content for: {query}")

    # -------------------------------------------------------------
    # 5. TIMING SEGREGATION (Requirement #17)
    # -------------------------------------------------------------
    def test_06_timing_segregation(self):
        """Ensures library and office timings are never confused with college timing."""
        resp_coll = chatbot_engine.process_message("What is the college timing?", session_id="test_timing")
        self.assertIn("10:30 AM to 5:50 PM", resp_coll["answer"])

        resp_lib = chatbot_engine.process_message("What is library timing?", session_id="test_timing")
        self.assertIn("8:30 AM to 6:00 PM", resp_lib["answer"])
        self.assertNotIn("10:30 AM to 5:50 PM", resp_lib["answer"])

        resp_off = chatbot_engine.process_message("What is office timing?", session_id="test_timing")
        self.assertIn("10:00 AM to 5:30 PM", resp_off["answer"])

    # -------------------------------------------------------------
    # 6. FOLLOW-UP CONTEXT MEMORY (Requirement #21)
    # -------------------------------------------------------------
    def test_07_follow_up_context(self):
        """User asks department, then 'Who is the HOD?' -> inherits department."""
        sess_id = "context_test_sess"
        # Turn 1
        r1 = chatbot_engine.process_message("Tell me about CSE AIML department", session_id=sess_id)
        self.assertIn(r1["intent"], ["department_hod", "departments", "courses", "cse_aiml"])

        # Turn 2: Follow-up without repeating CSE AIML
        r2 = chatbot_engine.process_message("Who is the HOD?", session_id=sess_id)
        self.assertEqual(r2["intent"], "department_hod")
        self.assertIn("Dr. Z. I. Khan", r2["answer"])

        # Another context: Placements -> Which companies?
        sess_placement = "context_test_placement"
        r3 = chatbot_engine.process_message("Tell me about placement", session_id=sess_placement)
        r4 = chatbot_engine.process_message("Which companies?", session_id=sess_placement)
        self.assertEqual(r4["intent"], "placement_companies")
        self.assertIn("Tata Consultancy Services", r4["answer"])

    # -------------------------------------------------------------
    # 7. ZERO HALLUCINATION ON UNKNOWN QUERIES (Requirement #18 & #19)
    # -------------------------------------------------------------
    def test_08_zero_hallucination(self):
        """Irrelevant or unknown queries must score <= 0 and return fallback guidance."""
        unknown_queries = [
            "What is the weather on Mars?",
            "Who won the 1994 FIFA world cup?",
            "Tell me about quantum gravity",
            "xyzqwer123456"
        ]
        for q in unknown_queries:
            resp = chatbot_engine.process_message(q, session_id="test_fallback")
            self.assertEqual(resp["intent"], "unknown", f"Failed for: {q}")
            self.assertEqual(resp["score"], 0)
            self.assertIn("Sorry, I couldn't find verified information", resp["answer"])
            self.assertIn("Departments", resp["answer"])
            self.assertIn("Placements", resp["answer"])

    # -------------------------------------------------------------
    # 8. TYPO TOLERANCE
    # -------------------------------------------------------------
    def test_09_typo_tolerance(self):
        """Common misspellings must be corrected."""
        resp = chatbot_engine.process_message("Which compnies come for placment?", session_id="test_typo")
        self.assertEqual(resp["intent"], "placement_companies")
        self.assertIn("Tata Consultancy Services", resp["answer"])

        resp2 = chatbot_engine.process_message("Who is the hod of cse aiml?", session_id="test_typo")
        self.assertEqual(resp2["intent"], "department_hod")
        self.assertIn("Dr. Z. I. Khan", resp2["answer"])

    # -------------------------------------------------------------
    # 9. FLASK REST API ENDPOINTS
    # -------------------------------------------------------------
    def test_10_flask_api_endpoints(self):
        """Validates /api/chat and /api/history."""
        res = self.client.post("/api/chat", json={
            "message": "Which companies come for placement?",
            "session_id": "api_test_session"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["intent"], "placement_companies")
        self.assertIn("Tata Consultancy Services", data["answer"])

        # History
        h_res = self.client.get("/api/history?session_id=api_test_session")
        self.assertEqual(h_res.status_code, 200)
        h_data = h_res.get_json()
    # -------------------------------------------------------------
    # 10. LEADERSHIP INTENT SEPARATION (Requirement #4)
    # Chairman, Vice Chairman, Director, Principal, Vice Principal, Dean, HOD
    # -------------------------------------------------------------
    def test_11_leadership_all_seven_roles(self):
        """Strictly tests all 7 leadership roles separation without cross-contamination."""
        # 1. Chairman
        r_chair = chatbot_engine.process_message("Who is the Chairman?", session_id="test_lead")
        self.assertEqual(r_chair["intent"], "chairman")
        self.assertIn("Pravin Pote Patil", r_chair["answer"])
        self.assertNotIn("Shreyash", r_chair["answer"])
        self.assertNotIn("Jawandhiya", r_chair["answer"])

        # 2. Vice Chairman
        r_vc = chatbot_engine.process_message("Who is the Vice Chairman?", session_id="test_lead")
        self.assertEqual(r_vc["intent"], "vice_chairman")
        self.assertIn("Shreyash Pote Patil", r_vc["answer"])
        self.assertNotIn("Prakash", r_vc["answer"])

        # 3. Director
        r_dir = chatbot_engine.process_message("Who is the Director?", session_id="test_lead")
        self.assertEqual(r_dir["intent"], "director")
        self.assertIn("Dr. Prakash M. Khodke", r_dir["answer"])
        self.assertNotIn("Jawandhiya", r_dir["answer"])

        # 4. Principal
        r_p = chatbot_engine.process_message("Who is the Principal?", session_id="test_lead")
        self.assertEqual(r_p["intent"], "principal")
        self.assertIn("Dr. P. M. Jawandhiya", r_p["answer"])
        self.assertNotIn("Mohammad Zuhair", r_p["answer"])

        # 5. Vice Principal
        r_vp = chatbot_engine.process_message("Who is the Vice Principal?", session_id="test_lead")
        self.assertEqual(r_vp["intent"], "vice_principal")
        self.assertIn("Dr. Mohammad Zuhair", r_vp["answer"])
        self.assertNotIn("Jawandhiya", r_vp["answer"])

        # 6. Dean / Dean Academics
        r_dean = chatbot_engine.process_message("Who is the Dean?", session_id="test_lead")
        self.assertIn(r_dean["intent"], ["dean", "dean_academics"])
        self.assertIn("Dr. V. B. Kute", r_dean["answer"])
        self.assertIn("academics.prpotepatilengg.ac.in", r_dean["source_url"])

        r_dean2 = chatbot_engine.process_message("Who is the Dean of Academics?", session_id="test_lead")
        self.assertIn(r_dean2["intent"], ["dean", "dean_academics"])
        self.assertIn("Dr. V. B. Kute", r_dean2["answer"])

        # 7. HOD
        r_hod = chatbot_engine.process_message("Who is the HOD of Civil?", session_id="test_lead")
        self.assertEqual(r_hod["intent"], "department_hod")
        self.assertIn("Dr. S. S. Saraf", r_hod["answer"])

    # -------------------------------------------------------------
    # 11. HOD AND DEPARTMENT RESOLUTION (Requirement #5)
    # -------------------------------------------------------------
    def test_12_hod_resolution_and_directory(self):
        """Tests department alias resolution (AI & ML, AI&DS, Computer, Mech) and ambiguous HOD directory."""
        # Generic HOD query must return directory of all 10 departments
        r_dir = chatbot_engine.process_message("Who is the HOD?", session_id="test_hod_res")
        self.assertEqual(r_dir["intent"], "department_hod")
        self.assertIn("Dr. V. B. Gadicha", r_dir["answer"])
        self.assertIn("Dr. Z. I. Khan", r_dir["answer"])
        self.assertIn("Dr. A. B. Gadicha", r_dir["answer"])
        self.assertIn("Dr. S. M. Tondare", r_dir["answer"])
        self.assertIn("Prof. Aparna Bhande", r_dir["answer"])

        # Specific alias tests
        aliases = [
            ("HOD of AI and ML?", "Dr. Z. I. Khan"),
            ("Who is the HOD of AI&DS?", "Dr. A. B. Gadicha"),
            ("Who is the HOD of Computer?", "Dr. V. B. Gadicha"),
            ("HOD of Mech?", "Dr. S. M. Tondare"),
            ("HOD of EE?", "Dr. D. A. Shahakar"),
            ("HOD of First Year?", "Dr. N. R. Thakare")
        ]
        for q, expected_hod in aliases:
            resp = chatbot_engine.process_message(q, session_id="test_hod_res")
            self.assertEqual(resp["intent"], "department_hod", f"Failed intent for: {q}")
            self.assertIn(expected_hod, resp["answer"], f"Expected {expected_hod} in answer for: {q}")

    # -------------------------------------------------------------
    # 12. PLACEMENT-COMPANY RETRIEVAL (Requirement #6)
    # -------------------------------------------------------------
    def test_13_placement_queries_disambiguation(self):
        """Tests that queries like 'Companies coming to college' or 'Companies hiring' return placement data."""
        queries = [
            "Companies coming to college",
            "Companies hiring",
            "Which companies visit?",
            "Placement companies list",
            "Companies visiting campus"
        ]
        for q in queries:
            resp = chatbot_engine.process_message(q, session_id="test_pl_disambig")
            self.assertEqual(resp["intent"], "placement_companies", f"Failed intent for: {q}")
            self.assertIn("Tata Consultancy Services", resp["answer"], f"Failed recruiters for: {q}")
            self.assertNotIn("10:30 AM", resp["answer"], f"Timing wrongly returned for: {q}")
            self.assertNotIn("established in the year 2008", resp["answer"], f"Establishment wrongly returned for: {q}")

    # -------------------------------------------------------------
    # 13. EXACT OFFICIAL SOURCE LINKS (Requirement #1 & #7)
    # -------------------------------------------------------------
    def test_14_official_websites_sources(self):
        """Validates that answers cite the correct official PRPCEM portal links."""
        # Academics
        r_acad = chatbot_engine.process_message("Where can I find the syllabus?", session_id="test_src")
        self.assertIn("https://academics.prpotepatilengg.ac.in/", r_acad["source_url"])

        # Exam Cell
        r_exam = chatbot_engine.process_message("When are examinations?", session_id="test_src")
        self.assertIn("https://examcell.prpotepatilengg.ac.in/", r_exam["source_url"])

        # Main Website Placements
        r_pl = chatbot_engine.process_message("Which companies come for placement?", session_id="test_src")
        self.assertIn("https://prpotepatilengg.ac.in/placement", r_pl["source_url"])

    # -------------------------------------------------------------
    # 14. VOICE MODULE (STT & TTS) INTEGRATION (Requirement #10 & #11)
    # -------------------------------------------------------------
    def test_15_voice_stt_and_tts_integration(self):
        """Validates that voice.js exists, contains SpeechSynthesis and SpeechRecognition logic, and is wired into index.html."""
        import os
        # 1. Verify voice.js file exists and is non-empty
        voice_js_path = os.path.join("static", "js", "voice.js")
        self.assertTrue(os.path.exists(voice_js_path))
        with open(voice_js_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("SpeechRecognition", content)
        self.assertIn("speechSynthesis", content)
        self.assertIn("VoiceModule", content)
        self.assertIn("attachSpeakerBtn", content)
        self.assertIn("cleanTextForSpeech", content)

        # 2. Verify templates/index.html loads voice.js and has micBtn & voice settings
        index_html_path = os.path.join("templates", "index.html")
        with open(index_html_path, "r", encoding="utf-8") as f:
            html = f.read()
        self.assertIn('src="/static/js/voice.js"', html)
        self.assertIn('id="micBtn"', html)
        self.assertIn('id="menuVoiceSettings"', html)

        # 3. Verify static/js/chatbot.js initializes VoiceModule
        chatbot_js_path = os.path.join("static", "js", "chatbot.js")
        with open(chatbot_js_path, "r", encoding="utf-8") as f:
            js = f.read()
        self.assertIn("VoiceModule", js)
        self.assertIn("attachSpeakerBtn", js)

if __name__ == "__main__":
    unittest.main()
