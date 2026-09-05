"""
PRPCEM College Assistant - Chatbot Engine
Intent-First, Entity-Aware Conversational Pipeline.
Strictly Zero ML, Zero LLM API.
"""

import re
from datetime import datetime
from database.database import (
    get_db_connection,
    log_chat_interaction,
    search_cutoffs,
    get_latest_cutoff_year,
    get_setting
)
from chatbot.intent_rules import detect_intent
from chatbot.keyword_matcher import normalize_text, extract_entities, DEPARTMENT_MAP
from chatbot.relevance import correct_typos, score_document
from chatbot.synonym import get_canonical_term, get_synonyms_for
from chatbot.response_generator import (
    format_cutoff_response,
    format_verified_answer,
    format_page_answer,
    format_document_answer,
    format_fallback_response
)

class ChatbotEngine:
    def __init__(self):
        # Session context for follow-up questions (No ML)
        self.session_contexts = {}

    def get_context(self, session_id):
        if not session_id:
            return {}
        return self.session_contexts.get(session_id, {})

    def update_context(self, session_id, **kwargs):
        if not session_id:
            return
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {}
        self.session_contexts[session_id].update(kwargs)

    def process_message(self, user_message, session_id="default"):
        """
        Intent-First Processing Pipeline:
        Step 1: Clean and normalize question.
        Step 2: Detect intent.
        Step 3: Detect important entities/fields (Department, Role, Year, Category).
        Step 4: Resolve follow-up session context.
        Step 5: Search relevant database records with negative penalties.
        Step 6: Return the highest-confidence verified answer.
        Step 7: If confidence is low, fallback safely without hallucination.
        """
        if not user_message or not user_message.strip():
            return {
                "answer": "Please ask a question about PRPCEM college.",
                "source": "Official College Assistant",
                "source_url": "https://prpotepatilengg.ac.in/",
                "intent": "empty",
                "score": 0,
                "card_type": "text",
                "card_data": None
            }

        raw_query = user_message.strip()

        # Step 1: Typo Correction & Normalization
        corrected_query = correct_typos(raw_query)
        normalized = normalize_text(corrected_query)

        # Step 2: Intent Classification
        intent, confidence = detect_intent(corrected_query)

        # Step 3: Entity Extraction
        entities = extract_entities(corrected_query)

        # Step 4: Follow-up Context Resolution (Requirement #21)
        context = self.get_context(session_id)

        # Follow-up: Inherit department if query doesn't specify one
        if not entities["department"] and context.get("last_department"):
            if intent in ("department_hod", "faculty_list", "cutoff", "fees", "eligibility", "departments", "courses", "syllabus"):
                entities["department"] = context["last_department"]
                entities["department_canonical"] = context["last_department_canonical"]

        # Follow-up: "Which companies?" after asking about placement
        if intent == "unknown" or intent == "placement_companies":
            if context.get("last_intent") in ("placement", "placement_companies", "placement_statistics", "training_placement"):
                if any(w in normalized for w in ["which", "companies", "recruiters", "who", "package"]):
                    intent = "placement_companies"

        # Update context
        if entities["department"]:
            self.update_context(
                session_id,
                last_department=entities["department"],
                last_department_canonical=entities["department_canonical"],
                last_intent=intent
            )
        elif intent != "unknown":
            self.update_context(session_id, last_intent=intent)

        # -------------------------------------------------------------
        # BRANCH A: DEDICATED CUTOFF SEARCH
        # -------------------------------------------------------------
        if intent in ("cutoff", "cap_round") or "cutoff" in normalized or "cut off" in normalized:
            cutoff_resp = self._handle_cutoff_query(entities, raw_query)
            log_chat_interaction(session_id, raw_query, cutoff_resp["answer"], cutoff_resp.get("source_url"))
            cutoff_resp["intent"] = "cutoff"
            cutoff_resp["score"] = 30
            return cutoff_resp

        # -------------------------------------------------------------
        # BRANCH B: COLLEGE TIMING (Strictly 10:30 AM to 5:50 PM - Requirement #9 & #17)
        # -------------------------------------------------------------
        if intent == "college_timing":
            timing_val = get_setting("college_timing", "10:30 AM to 5:50 PM")
            answer = f"PRPCEM's regular college timing is {timing_val}."
            resp = {
                "answer": answer,
                "source": "Verified College Information",
                "source_url": "https://prpotepatilengg.ac.in/",
                "intent": "college_timing",
                "score": 35,
                "card_type": "verified_card",
                "card_data": {
                    "category": "College Timing",
                    "timing": timing_val,
                    "verified": True
                }
            }
            log_chat_interaction(session_id, raw_query, answer, resp["source_url"])
            return resp

        conn = get_db_connection()

        # -------------------------------------------------------------
        # BRANCH B1: LEADERSHIP INTENTS (Requirement #4)
        # Chairman, Vice Chairman, Director, Principal, Vice Principal, Dean
        # -------------------------------------------------------------
        LEADERSHIP_CATEGORY_MAP = {
            "chairman": "chairman",
            "vice_chairman": "vice_chairman",
            "director": "director",
            "principal": "principal",
            "vice_principal": "vice_principal",
            "dean": "dean_academics",
            "dean_academics": "dean_academics"
        }
        if intent in LEADERSHIP_CATEGORY_MAP:
            target_cat = LEADERSHIP_CATEGORY_MAP[intent]
            leader_row = conn.execute(
                "SELECT * FROM knowledge WHERE category = ?",
                (target_cat,)
            ).fetchone()
            if leader_row:
                formatted = format_verified_answer(leader_row)
                formatted["intent"] = intent
                formatted["score"] = 40
                log_chat_interaction(session_id, raw_query, formatted["answer"], formatted["source_url"])
                conn.close()
                return formatted

        # -------------------------------------------------------------
        # BRANCH B2: HOD INTENT RESOLUTION (Requirement #4 & #5)
        # -------------------------------------------------------------
        if intent == "department_hod":
            query_dept = entities["department_canonical"]
            if query_dept:
                hod_row = conn.execute(
                    "SELECT * FROM knowledge WHERE category = 'department_hod' AND department = ?",
                    (query_dept,)
                ).fetchone()
                if not hod_row:
                    hod_row = conn.execute(
                        "SELECT * FROM knowledge WHERE category = 'department_hod' AND (department LIKE ? OR keyword LIKE ?)",
                        (f"%{query_dept}%", f"%{entities['department']}%")
                    ).fetchone()
                if hod_row:
                    formatted = format_verified_answer(hod_row)
                    formatted["intent"] = "department_hod"
                    formatted["score"] = 40
                    log_chat_interaction(session_id, raw_query, formatted["answer"], formatted["source_url"])
                    conn.close()
                    return formatted

            # If no specific department was identified:
            hod_summary = (
                "PRPCEM has 10 academic departments, each led by an experienced Head of Department (HOD):\n\n"
                "• **Computer Science & Engineering (CSE):** Dr. V. B. Gadicha\n"
                "• **CSE (Artificial Intelligence & Machine Learning):** Dr. Z. I. Khan\n"
                "• **Artificial Intelligence & Data Science (AI&DS):** Dr. A. B. Gadicha\n"
                "• **Electronics & Telecommunication (EXTC):** Dr. U. W. Hore\n"
                "• **Electrical Engineering:** Dr. D. A. Shahakar\n"
                "• **Mechanical Engineering:** Dr. S. M. Tondare\n"
                "• **Civil Engineering:** Dr. S. S. Saraf\n"
                "• **Applied Science & Humanities (First Year / AS&H):** Dr. N. R. Thakare\n"
                "• **MBA (Department of Management Studies):** Prof. S. R. Shah\n"
                "• **MCA (Master of Computer Applications):** Prof. Aparna Bhande\n\n"
                "You can ask about a specific department (e.g. *'Who is the HOD of Mechanical?'*) for direct department details."
            )
            resp = {
                "answer": hod_summary,
                "source": "PRPCEM Official Website",
                "source_url": "https://prpotepatilengg.ac.in/academics",
                "intent": "department_hod",
                "score": 35,
                "card_type": "verified_card",
                "card_data": {
                    "category": "department_hod",
                    "verified": True
                }
            }
            log_chat_interaction(session_id, raw_query, resp["answer"], resp["source_url"])
            conn.close()
            return resp

        # -------------------------------------------------------------
        # BRANCH B3: PLACEMENT RECRUITERS & COMPANIES (Requirement #6 & #7)
        # -------------------------------------------------------------
        if intent == "placement_companies":
            placement_row = conn.execute(
                "SELECT * FROM knowledge WHERE category = 'placement_companies'"
            ).fetchone()
            if placement_row:
                formatted = format_verified_answer(placement_row)
                formatted["intent"] = "placement_companies"
                formatted["score"] = 40
                log_chat_interaction(session_id, raw_query, formatted["answer"], formatted["source_url"])
                conn.close()
                return formatted

        # -------------------------------------------------------------
        # BRANCH C: VERIFIED KNOWLEDGE BASE SEARCH
        # Intent-category mapping ensures leadership queries only match their correct category
        # -------------------------------------------------------------

        # Map intents directly to database category for fast, exact retrieval
        INTENT_CATEGORY_MAP = {
            "chairman": ["chairman"],
            "vice_chairman": ["vice_chairman"],
            "director": ["director"],
            "principal": ["principal"],
            "vice_principal": ["vice_principal"],
            "dean": ["dean_academics"],
            "dean_academics": ["dean_academics"],
            "department_hod": ["department_hod"],
            "placement_companies": ["placement_companies"],
            "placement_statistics": ["placement_statistics", "placement"],
            "training_placement": ["training_placement", "placement_statistics"],
            "college_timing": ["college_timing"],
            "office_timing": ["office_timing"],
            "library_timing": ["library_timing"],
            "examination": ["examination"],
            "syllabus": ["syllabus"],
            "academic_calendar": ["academic_calendar"],
            "hostel": ["hostel"],
            "library": ["library"],
            "facilities": ["facilities"],
            "contact": ["contact"],
            "location": ["location"],
            "fees": ["fees", "scholarship"],
            "documents": ["documents"],
            "admission_process": ["admission_process", "documents"],
            "eligibility": ["eligibility", "admission_process"],
            "cutoff": ["cutoff"],
            "departments": ["departments"],
            "courses": ["courses"],
            "college_establishment": ["college_establishment"],
            "about_college": ["about_college", "college_establishment"],
            "faculty_list": ["faculty_list", "department_hod"],
            "scholarship": ["scholarship", "fees"],
        }

        # Try category-restricted search first for leadership & sensitive intents
        targeted_categories = INTENT_CATEGORY_MAP.get(intent)
        knowledge_candidates = []
        if targeted_categories:
            placeholders = ",".join(["?"] * len(targeted_categories))
            knowledge_candidates = conn.execute(
                f"SELECT * FROM knowledge WHERE category IN ({placeholders})",
                targeted_categories
            ).fetchall()

        # If no targeted candidates, fall back to all knowledge
        if not knowledge_candidates:
            knowledge_candidates = conn.execute("SELECT * FROM knowledge").fetchall()

        best_knowledge = None
        best_score = -99

        query_dept = entities["department_canonical"]
        query_year = entities["year"]

        for row in knowledge_candidates:
            sc = score_document(
                query=corrected_query,
                doc_title=row["question"],
                doc_headings=row["keyword"],
                doc_content=row["answer"],
                doc_category=row["category"],
                matched_intent=intent,
                doc_dept=row["department"],
                query_dept=query_dept,
                doc_year=row["academic_year"],
                query_year=query_year
            )

            # Verified bonus applies ONLY if the candidate has positive relevance (sc >= 8)
            if sc >= 8 and row["verified"]:
                sc += 12

            if sc > best_score:
                best_score = sc
                best_knowledge = row

        # If high-confidence knowledge match found (threshold >= 15)
        if best_knowledge and best_score >= 15:
            formatted = format_verified_answer(best_knowledge)
            formatted["intent"] = best_knowledge["category"]
            formatted["score"] = best_score
            log_chat_interaction(session_id, raw_query, formatted["answer"], formatted["source_url"])
            conn.close()
            return formatted

        # -------------------------------------------------------------
        # BRANCH D: CRAWLED PAGES & DOCUMENTS SEARCH
        # -------------------------------------------------------------
        pages = conn.execute("SELECT * FROM pages").fetchall()
        best_page = None
        best_page_score = -99

        for p in pages:
            sc = score_document(
                query=corrected_query,
                doc_title=p["title"],
                doc_headings="",
                doc_content=p["content"],
                doc_category=p["category"],
                matched_intent=intent,
                doc_dept=p.get("department") if hasattr(p, "keys") and "department" in p.keys() else None,
                query_dept=query_dept
            )
            if sc > best_page_score:
                best_page_score = sc
                best_page = p

        docs = conn.execute("SELECT * FROM documents").fetchall()
        best_doc = None
        best_doc_score = -99

        for d in docs:
            sc = score_document(
                query=corrected_query,
                doc_title=d["title"],
                doc_headings="",
                doc_content=d["content"],
                doc_category=d["category"],
                matched_intent=intent
            )
            if sc > best_doc_score:
                best_doc_score = sc
                best_doc = d

        conn.close()

        # Check if scraped page or document qualifies with high confidence (>= 18)
        if best_page and best_page_score >= 18 and best_page_score >= best_doc_score:
            formatted = format_page_answer(best_page)
            formatted["intent"] = intent if intent != "unknown" else "web_page"
            formatted["score"] = best_page_score
            log_chat_interaction(session_id, raw_query, formatted["answer"], formatted["source_url"])
            return formatted

        if best_doc and best_doc_score >= 18:
            formatted = format_document_answer(best_doc)
            formatted["intent"] = intent if intent != "unknown" else "pdf_document"
            formatted["score"] = best_doc_score
            log_chat_interaction(session_id, raw_query, formatted["answer"], formatted["source_url"])
            return formatted

        # -------------------------------------------------------------
        # BRANCH E: NO HALLUCINATION FALLBACK (Requirement #18, #19, #26)
        # -------------------------------------------------------------
        fallback = format_fallback_response()
        fallback["intent"] = "unknown"
        fallback["score"] = 0
        log_chat_interaction(session_id, raw_query, fallback["answer"], fallback["source_url"])
        return fallback

    def _handle_cutoff_query(self, entities, raw_query):
        """Dedicated cutoff lookup logic supporting Year, Branch, Round, and Category."""
        branch_name = entities["department_canonical"] or "Computer Science and Engineering"
        category = entities["category"] or "OPEN"
        cap_round = entities["cap_round"]
        year = entities["year"]

        if entities["is_latest"] or not year:
            year = get_latest_cutoff_year()

        results = search_cutoffs(
            branch=branch_name,
            category=category,
            cap_round=cap_round,
            academic_year=year
        )

        if not results:
            results = search_cutoffs(branch=branch_name, academic_year=year)

        if not results:
            results = search_cutoffs(branch=branch_name)

        if not results:
            return {
                "answer": f"Latest verified cutoff information was not found for {branch_name}.",
                "source": "Official Admission Authority",
                "source_url": "https://fe2025.mahacet.org/",
                "card_type": "text",
                "card_data": None
            }

        return format_cutoff_response(
            cutoffs=results,
            branch_name=branch_name,
            requested_year=year,
            requested_round=cap_round
        )

# Global singleton instance
chatbot_engine = ChatbotEngine()
