"""
PRPCEM College Assistant - Response Generator
Generates structured answers, cutoff cards, timing cards, and verified sources.
Strictly adheres to deterministic template generation without ML hallucinations.
"""

CUTOFF_DISCLAIMER = (
    "Cutoffs may vary by admission year, CAP round, category, quota, "
    "seat availability and admission rules. Please verify the latest official "
    "information before making admission decisions."
)

FALLBACK_MESSAGE = (
    "Sorry, I couldn't find verified information about this in the available official PRPCEM information.\n\n"
    "You can ask me about:\n"
    "• Admissions\n"
    "• Courses\n"
    "• Cutoff\n"
    "• College Timing\n"
    "• Fees\n"
    "• Departments\n"
    "• Examination\n"
    "• Placements\n"
    "• Hostel\n"
    "• Contact"
)

def format_cutoff_response(cutoffs, branch_name=None, requested_year=None, requested_round=None):
    """
    Constructs a rich cutoff response with individual cards and official disclaimers.
    """
    if not cutoffs:
        return {
            "answer": f"No verified cutoff records found for the specified criteria.",
            "source": "Official Admission Authority",
            "source_url": "https://fe2025.mahacet.org/",
            "card_type": "text",
            "card_data": None
        }

    cards = []
    text_lines = []

    for c in cutoffs[:4]:  # Show top matching cards
        card = {
            "academic_year": c["academic_year"],
            "course": c.get("course", "B.Tech"),
            "branch": c["branch"],
            "category": c["category"],
            "quota": c.get("quota", "Home University"),
            "cap_round": c["cap_round"],
            "cutoff_type": c["cutoff_type"],
            "cutoff_value": c["cutoff_value"],
            "source_url": c["source_url"],
            "source_name": "Official Admission Authority Source" if "mahacet" in c["source_url"] else "PRPCEM Official Verified Source"
        }
        cards.append(card)

    first = cutoffs[0]
    summary_text = (
        f"Here is the verified cutoff information for **{first['branch']}** "
        f"({first['academic_year']}, CAP Round {first['cap_round']}, {first['category']} Category):\n\n"
        f"• **Cutoff Type:** {first['cutoff_type']}\n"
        f"• **Cutoff Value:** {first['cutoff_value']}\n"
        f"• **Quota:** {first.get('quota', 'Home University')}\n\n"
        f"*{CUTOFF_DISCLAIMER}*"
    )

    return {
        "answer": summary_text,
        "source": first.get("source_name", "Official Admission Authority"),
        "source_url": first["source_url"],
        "card_type": "cutoff_card",
        "card_data": cards,
        "disclaimer": CUTOFF_DISCLAIMER
    }

def format_verified_answer(knowledge_row):
    """Formats verified information directly from knowledge base."""
    row = dict(knowledge_row) if hasattr(knowledge_row, "keys") else knowledge_row
    source_url = row.get("source_url") or "https://prpotepatilengg.ac.in/"
    source_label = "Verified College Information"
    if "mahacet" in source_url:
        source_label = "Official Admission Authority"
    elif "prpotepatilengg" in source_url:
        source_label = "PRPCEM Official Website"

    return {
        "answer": row["answer"],
        "source": source_label,
        "source_url": source_url,
        "card_type": "verified_card",
        "card_data": {
            "category": row.get("category", "College Information"),
            "verified": bool(row.get("verified", 1)),
            "last_updated": row.get("last_updated", "")
        }
    }

def format_page_answer(page_row):
    """Formats answer extracted from crawled web page."""
    row = dict(page_row) if hasattr(page_row, "keys") else page_row
    content = row["content"]
    # Take first 3-4 clean paragraphs or up to 450 characters
    paragraphs = [p.strip() for p in content.split("\n") if len(p.strip()) > 30]
    excerpt = "\n\n".join(paragraphs[:3]) if paragraphs else content[:450]

    return {
        "answer": excerpt,
        "source": "PRPCEM Official Website",
        "source_url": row["url"],
        "card_type": "page_card",
        "card_data": {
            "title": row.get("title", "PRPCEM Page"),
            "category": row.get("category", "General")
        }
    }

def format_document_answer(doc_row):
    """Formats answer extracted from official PDF."""
    row = dict(doc_row) if hasattr(doc_row, "keys") else doc_row
    content = row["content"]
    paragraphs = [p.strip() for p in content.split("\n") if len(p.strip()) > 30]
    excerpt = "\n\n".join(paragraphs[:3]) if paragraphs else content[:400]

    return {
        "answer": excerpt,
        "source": "Official PRPCEM Document",
        "source_url": row["url"],
        "card_type": "document_card",
        "card_data": {
            "title": row.get("title", "Official PRPCEM Document"),
            "category": row.get("category", "Official Document")
        }
    }

def format_fallback_response():
    """Returns strict fallback response when no verified data exists."""
    return {
        "answer": FALLBACK_MESSAGE,
        "source": "Official College Information Assistant",
        "source_url": "https://prpotepatilengg.ac.in/",
        "card_type": "fallback",
        "card_data": None
    }
