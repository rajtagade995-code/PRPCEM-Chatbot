"""
PRPCEM College Assistant - Flask Application
Standalone, Rule-Based College Information Assistant
Official Assistant for: P. R. Pote Patil College of Engineering & Management, Amravati
"""

import os
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, session,
    redirect, url_for, flash
)
from werkzeug.security import check_password_hash
import config
from database.database import (
    init_db, get_db_connection, get_setting, set_setting,
    get_session_history, get_all_chat_sessions, delete_chat_session,
    clear_all_chat_history, generate_coverage_report
)
from crawler.crawler import crawler_instance
from chatbot.chatbot_engine import chatbot_engine

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Ensure database is initialized at startup
init_db()

@app.after_request
def add_cors_headers(response):
    """Enable CORS for embedding and external API access."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

@app.route("/health")
@app.route("/api/health")
def health_check():
    """Production health check endpoint."""
    return jsonify({"status": "healthy", "service": "PRPCEM College Assistant"}), 200

def admin_required(f):
    """Decorator to enforce admin authentication on dashboard and API routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            if request.is_json or request.path.startswith("/api/admin"):
                return jsonify({"error": "Unauthorized. Please log in."}), 401
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

# =========================================================================
# PUBLIC USER ROUTES
# =========================================================================

@app.route("/")
def index():
    """Main Standalone Chatbot Interface."""
    college_info = {
        "name": config.COLLEGE_NAME,
        "short_name": config.COLLEGE_SHORT_NAME,
        "website": config.COLLEGE_WEBSITE,
        "timing": get_setting("college_timing", config.DEFAULT_COLLEGE_TIMING),
        "phone": get_setting("college_phone", "9371132222"),
        "email": get_setting("college_email", "principal@prpotepatilengg.ac.in")
    }
    return render_template("index.html", college=college_info)

@app.route("/history")
def history_page():
    """Standalone Conversation History View."""
    return render_template("history.html")

@app.route("/widget")
@app.route("/embed")
def widget_page():
    """Official College Website Integration Snippet."""
    return render_template("widget_snippet.html")

# =========================================================================
# CHAT & HISTORY APIS
# =========================================================================

@app.route("/api/chat", methods=["POST"])
def chat_api():
    """
    Primary API Endpoint (Requirement #54)
    Request: { "message": "What is the CSE cutoff?", "session_id": "abc123" }
    Response: { "answer": "...", "source": "...", "source_url": "...", "intent": "cutoff", "score": 30 }
    """
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    user_message = data.get("message", "").strip()
    session_id = data.get("session_id", "default_session").strip()

    if not user_message:
        return jsonify({
            "answer": "Please type a question about PRPCEM college.",
            "source": "Official College Assistant",
            "source_url": config.COLLEGE_WEBSITE,
            "intent": "empty",
            "score": 0,
            "card_type": "text",
            "card_data": None
        })

    response = chatbot_engine.process_message(user_message, session_id=session_id)
    return jsonify(response)

@app.route("/api/history", methods=["GET"])
def get_history_api():
    """Retrieves session list or specific session messages."""
    session_id = request.args.get("session_id")
    if session_id:
        messages = get_session_history(session_id)
        return jsonify({"session_id": session_id, "messages": messages})

    sessions_list = get_all_chat_sessions()
    return jsonify({"sessions": sessions_list})

@app.route("/api/history/<session_id>", methods=["DELETE"])
def delete_history_api(session_id):
    """Deletes a specific session conversation history."""
    delete_chat_session(session_id)
    return jsonify({"success": True, "message": "Session history cleared."})

@app.route("/api/history", methods=["DELETE"])
def clear_all_history_api():
    """Clears all conversations."""
    clear_all_chat_history()
    return jsonify({"success": True, "message": "All chat history cleared."})

# =========================================================================
# ADMIN AUTHENTICATION
# =========================================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Secure Admin Login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        conn = get_db_connection()
        admin_row = conn.execute(
            "SELECT * FROM admins WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if admin_row and check_password_hash(admin_row["password_hash"], password):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            flash("Welcome back, Administrator.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid administrator credentials.", "danger")

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    """Admin Logout."""
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    flash("You have been securely logged out.", "info")
    return redirect(url_for("admin_login"))

# =========================================================================
# ADMIN DASHBOARD & CONTROLS
# =========================================================================

@app.route("/admin")
@admin_required
def admin_dashboard():
    """Main Admin Dashboard."""
    return render_template("admin.html")

@app.route("/api/admin/stats", methods=["GET"])
@admin_required
def admin_stats_api():
    """Returns real-time dashboard statistics."""
    conn = get_db_connection()
    total_pages = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
    total_pdfs = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    total_knowledge = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    total_cutoffs = conn.execute("SELECT COUNT(*) FROM cutoffs").fetchone()[0]
    total_chats = conn.execute("SELECT COUNT(*) FROM chat_history").fetchone()[0]
    conn.close()

    last_crawl = get_setting("last_crawl_time", "Never")

    return jsonify({
        "total_pages": total_pages,
        "total_pdfs": total_pdfs,
        "total_knowledge": total_knowledge,
        "total_cutoffs": total_cutoffs,
        "total_chats": total_chats,
        "last_crawl": last_crawl
    })

# --- Crawler APIs ---

@app.route("/api/admin/crawler/start", methods=["POST"])
@admin_required
def start_crawler_api():
    """Starts the crawler."""
    data = request.get_json() or {}
    max_pages = data.get("max_pages", config.MAX_PAGES)
    max_depth = data.get("max_depth", config.MAX_DEPTH)

    success, msg = crawler_instance.start_crawl(max_pages=max_pages, max_depth=max_depth)
    return jsonify({"success": success, "message": msg})

@app.route("/api/admin/crawler/update", methods=["POST"])
@admin_required
def update_website_data_api():
    """Triggers change-detection crawl updating modified pages via content_hash."""
    success, msg = crawler_instance.start_crawl(update_mode=True)
    return jsonify({"success": success, "message": msg})

@app.route("/api/admin/crawler/stop", methods=["POST"])
@admin_required
def stop_crawler_api():
    """Stops the active crawl."""
    success, msg = crawler_instance.stop_crawl()
    return jsonify({"success": success, "message": msg})

@app.route("/api/admin/crawler/status", methods=["GET"])
@admin_required
def crawler_status_api():
    """Returns live crawler progress."""
    return jsonify(crawler_instance.get_status())

@app.route("/api/admin/coverage-report", methods=["GET"])
@admin_required
def coverage_report_api():
    """Returns knowledge coverage metrics across categories."""
    report = generate_coverage_report()
    return jsonify(report)

# --- Knowledge Base CRUD ---

@app.route("/api/admin/knowledge", methods=["GET", "POST", "PUT", "DELETE"])
@admin_required
def admin_knowledge_api():
    conn = get_db_connection()

    if request.method == "GET":
        rows = conn.execute("SELECT * FROM knowledge ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify({"knowledge": [dict(r) for r in rows]})

    elif request.method == "POST":
        data = request.get_json() or {}
        conn.execute(
            """INSERT INTO knowledge (question, keyword, category, subcategory, department, academic_year, answer, source_url, verified)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("question", "").strip(),
                data.get("keyword", "").strip(),
                data.get("category", "General").strip(),
                data.get("subcategory", "General").strip(),
                data.get("department") or None,
                data.get("academic_year", "2025-26").strip(),
                data.get("answer", "").strip(),
                data.get("source_url", config.COLLEGE_WEBSITE).strip(),
                int(data.get("verified", 1))
            )
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Knowledge entry added successfully."})

    elif request.method == "PUT":
        data = request.get_json() or {}
        entry_id = data.get("id")
        conn.execute(
            """UPDATE knowledge SET question=?, keyword=?, category=?, subcategory=?, department=?, academic_year=?, answer=?, source_url=?, verified=?
               WHERE id = ?""",
            (
                data.get("question", "").strip(),
                data.get("keyword", "").strip(),
                data.get("category", "General").strip(),
                data.get("subcategory", "General").strip(),
                data.get("department") or None,
                data.get("academic_year", "2025-26").strip(),
                data.get("answer", "").strip(),
                data.get("source_url", config.COLLEGE_WEBSITE).strip(),
                int(data.get("verified", 1)),
                entry_id
            )
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Knowledge entry updated."})

    elif request.method == "DELETE":
        entry_id = request.args.get("id")
        conn.execute("DELETE FROM knowledge WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Knowledge entry deleted."})

# --- Cutoffs CRUD ---

@app.route("/api/admin/cutoffs", methods=["GET", "POST", "PUT", "DELETE"])
@admin_required
def admin_cutoffs_api():
    conn = get_db_connection()

    if request.method == "GET":
        rows = conn.execute(
            "SELECT * FROM cutoffs ORDER BY academic_year DESC, cap_round ASC, cutoff_value DESC"
        ).fetchall()
        conn.close()
        return jsonify({"cutoffs": [dict(r) for r in rows]})

    elif request.method == "POST":
        data = request.get_json() or {}
        conn.execute(
            """INSERT INTO cutoffs (academic_year, course, branch, category, quota, cap_round, cutoff_type, cutoff_value, source_url, source_date)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.get("academic_year", "2025-26").strip(),
                data.get("course", "B.Tech").strip(),
                data.get("branch", "").strip(),
                data.get("category", "OPEN").strip().upper(),
                data.get("quota", "Home University").strip(),
                int(data.get("cap_round", 1)),
                data.get("cutoff_type", "Percentile").strip(),
                data.get("cutoff_value", "").strip(),
                data.get("source_url", "https://fe2025.mahacet.org/").strip(),
                data.get("source_date", "").strip()
            )
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Cutoff record created."})

    elif request.method == "PUT":
        data = request.get_json() or {}
        cutoff_id = data.get("id")
        conn.execute(
            """UPDATE cutoffs SET academic_year=?, course=?, branch=?, category=?, quota=?,
                                cap_round=?, cutoff_type=?, cutoff_value=?, source_url=?, source_date=?
               WHERE id = ?""",
            (
                data.get("academic_year", "2025-26").strip(),
                data.get("course", "B.Tech").strip(),
                data.get("branch", "").strip(),
                data.get("category", "OPEN").strip().upper(),
                data.get("quota", "Home University").strip(),
                int(data.get("cap_round", 1)),
                data.get("cutoff_type", "Percentile").strip(),
                data.get("cutoff_value", "").strip(),
                data.get("source_url", "https://fe2025.mahacet.org/").strip(),
                data.get("source_date", "").strip(),
                cutoff_id
            )
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Cutoff record updated."})

    elif request.method == "DELETE":
        cutoff_id = request.args.get("id")
        conn.execute("DELETE FROM cutoffs WHERE id = ?", (cutoff_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Cutoff record deleted."})

# --- College Information Settings ---

@app.route("/api/admin/college-info", methods=["GET", "POST"])
@admin_required
def admin_college_info_api():
    if request.method == "GET":
        info = {
            "college_timing": get_setting("college_timing", config.DEFAULT_COLLEGE_TIMING),
            "office_timing": get_setting("office_timing", config.DEFAULT_OFFICE_TIMING),
            "library_timing": get_setting("library_timing", config.DEFAULT_LIBRARY_TIMING),
            "exam_office_timing": get_setting("exam_office_timing", config.DEFAULT_EXAM_OFFICE_TIMING),
            "admission_office_timing": get_setting("admission_office_timing", config.DEFAULT_ADMISSION_OFFICE_TIMING),
            "college_address": get_setting("college_address", config.COLLEGE_LOCATION),
            "college_phone": get_setting("college_phone", "9371132222, 9371142222, 9371152222"),
            "college_email": get_setting("college_email", "principal@prpotepatilengg.ac.in"),
            "admission_phone": get_setting("admission_phone", "9823962311, 9503611038"),
            "tpo_email": get_setting("tpo_email", "prpgei.verify@gmail.com")
        }
        return jsonify(info)

    elif request.method == "POST":
        data = request.get_json() or {}
        for key, val in data.items():
            set_setting(key, val)

        # Also update verified knowledge row for college timing if changed
        if "college_timing" in data:
            new_timing = data["college_timing"]
            conn = get_db_connection()
            conn.execute(
                """UPDATE knowledge SET answer = ? WHERE category = 'college_timing'""",
                (f"PRPCEM college timing is {new_timing}.",)
            )
            conn.commit()
            conn.close()

        return jsonify({"success": True, "message": "College information updated successfully."})

# --- Pages & Documents Viewers ---

@app.route("/api/admin/pages", methods=["GET", "DELETE"])
@admin_required
def admin_pages_api():
    conn = get_db_connection()
    if request.method == "GET":
        rows = conn.execute("SELECT id, url, title, category, last_crawled FROM pages ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify({"pages": [dict(r) for r in rows]})
    elif request.method == "DELETE":
        page_id = request.args.get("id")
        conn.execute("DELETE FROM pages WHERE id = ?", (page_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Page record deleted."})

@app.route("/api/admin/documents", methods=["GET", "DELETE"])
@admin_required
def admin_documents_api():
    conn = get_db_connection()
    if request.method == "GET":
        rows = conn.execute("SELECT id, url, title, category, last_crawled FROM documents ORDER BY id DESC").fetchall()
        conn.close()
        return jsonify({"documents": [dict(r) for r in rows]})
    elif request.method == "DELETE":
        doc_id = request.args.get("id")
        conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Document record deleted."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")
    app.run(host=host, port=port, debug=debug)
