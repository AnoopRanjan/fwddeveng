"""
Flask Web Application: FDE + AI + Cybersecurity Advisor Learning & Transformation Portal
Compatible with local execution (`python app.py`) and instant Vercel Serverless deployment.
"""

import os
import time
import shutil
import sqlite3
import tempfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, Response

from data.topics import TOPICS, get_topic_by_id
from data.roadmap import ROADMAP_DAYS, get_day_by_number, get_days_by_phase
from data.projects import PROJECTS, get_project_by_id
from data.kql_queries import KQL_QUERIES, MOCK_LOGS, get_kql_by_id
from data.interview_prep import POSITIONING_STRATEGY, ELEVATOR_PITCH, INTERVIEW_QUESTIONS, get_questions_by_category
from data.fde_masterclass import FDE_MASTER_COURSE, PROJECT_EXPLORATION_PILLARS, FDE_BRIEFING_10MIN
from data.outreach import parse_institutes_from_upload, generate_sales_email, get_sample_csv_template, SAMPLE_INSTITUTIONS, DEFAULT_SENDER, SIGN_OFF_NAME
from data.access_control import (
    create_access_request,
    verify_and_consume_passcode,
    get_request_by_token,
    approve_access_by_token,
    get_all_inbox_messages,
    ADMIN_EMAIL,
    ADMIN_NAME
)
from data.google_auth import (
    generate_pkce_pair,
    create_signed_oauth_state,
    verify_signed_oauth_state,
    get_google_authorization_url,
    parse_and_validate_jwt,
    exchange_oauth_code_for_user,
    login_user_session,
    logout_user_session,
    ADMIN_PASSWORD,
    verify_admin_password
)

# Base paths configuration for absolute directory resolution (essential for Vercel serverless)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = "fde-cyber-ai-advisor-portal-key-2026"

# Vercel environment detection: filesystem is read-only except tempdir (/tmp on Linux/Vercel)
IS_VERCEL = bool(os.environ.get("VERCEL"))
if IS_VERCEL:
    DB_DIR = tempfile.gettempdir()
else:
    DB_DIR = BASE_DIR

DB_PATH = os.path.join(DB_DIR, "learning_portal.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and seeds data. Safe to call repeatedly."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # If running on Vercel and DB doesn't exist in /tmp, copy bundled DB if present
    if IS_VERCEL and not os.path.exists(DB_PATH):
        bundled = os.path.join(BASE_DIR, "learning_portal.db")
        if os.path.exists(bundled):
            try:
                shutil.copyfile(bundled, DB_PATH)
            except Exception:
                pass

    conn = get_db()
    cursor = conn.cursor()
    
    # Progress for each of the 35 days
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS day_progress (
            day INTEGER PRIMARY KEY,
            completed INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            completed_at TEXT
        )
    """)
    
    # Progress for each of the 10 topics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS topic_progress (
            topic_id INTEGER PRIMARY KEY,
            status TEXT DEFAULT 'not_started',
            notes TEXT DEFAULT '',
            updated_at TEXT
        )
    """)

    # User general notes / lab journal
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            tag TEXT,
            created_at TEXT
        )
    """)

    # Access requests table (unique passcode & allow link tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            passcode TEXT NOT NULL,
            token TEXT NOT NULL UNIQUE,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL,
            approved_at TEXT,
            ip_address TEXT
        )
    """)

    # Simulated email inbox table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulated_inbox (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipient TEXT NOT NULL,
            sender TEXT NOT NULL,
            subject TEXT NOT NULL,
            body TEXT NOT NULL,
            token TEXT,
            passcode TEXT,
            sent_at TEXT NOT NULL,
            is_read INTEGER DEFAULT 0
        )
    """)

    # Authenticated Google SSO Users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_id TEXT UNIQUE,
            email TEXT UNIQUE NOT NULL,
            name TEXT,
            picture TEXT,
            role TEXT DEFAULT 'member',
            created_at TEXT NOT NULL,
            last_login_at TEXT NOT NULL
        )
    """)
    
    # Seed day_progress if empty
    cursor.execute("SELECT COUNT(*) as count FROM day_progress")
    if cursor.fetchone()["count"] == 0:
        for day in range(1, 36):
            cursor.execute("INSERT OR IGNORE INTO day_progress (day, completed, notes) VALUES (?, 0, '')", (day,))
            
    # Seed topic_progress if empty
    cursor.execute("SELECT COUNT(*) as count FROM topic_progress")
    if cursor.fetchone()["count"] == 0:
        for topic in TOPICS:
            cursor.execute("INSERT OR IGNORE INTO topic_progress (topic_id, status, notes) VALUES (?, 'not_started', '')", (topic["id"],))
            
    conn.commit()
    conn.close()


# Ensure database is initialized upon module load (critical for Vercel WSGI worker initialization)
try:
    init_db()
except Exception as e:
    print(f"Initial DB bootstrap notice: {e}")


def calculate_metrics():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Days completed
        cursor.execute("SELECT COUNT(*) as total, SUM(completed) as completed FROM day_progress")
        row = cursor.fetchone()
        total_days = row["total"] or 35
        completed_days = row["completed"] or 0
        days_percent = int((completed_days / total_days) * 100) if total_days else 0
        
        # Topics completed
        cursor.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed FROM topic_progress")
        t_row = cursor.fetchone()
        total_topics = t_row["total"] or 10
        completed_topics = t_row["completed"] or 0
        topics_percent = int((completed_topics / total_topics) * 100) if total_topics else 0
        
        # Find next active day
        cursor.execute("SELECT day FROM day_progress WHERE completed = 0 ORDER BY day ASC LIMIT 1")
        next_day_row = cursor.fetchone()
        current_day = next_day_row["day"] if next_day_row else 35
        
        conn.close()
        return {
            "total_days": total_days,
            "completed_days": completed_days,
            "days_percent": days_percent,
            "total_topics": total_topics,
            "completed_topics": completed_topics,
            "topics_percent": topics_percent,
            "current_day": current_day
        }
    except Exception:
        return {
            "total_days": 35,
            "completed_days": 0,
            "days_percent": 0,
            "total_topics": 10,
            "completed_topics": 0,
            "topics_percent": 0,
            "current_day": 1
        }


# Context processor to make metrics, authentication, and admin state available globally
@app.context_processor
def inject_global_metrics():
    user_email = (session.get("user_email") or "").strip().lower()
    admin_emails = [ADMIN_EMAIL.lower(), "azureanoopranjan@gmail.com"]
    is_admin = bool(session.get("is_admin", False) and user_email in admin_emails)
    is_logged_in = bool(user_email)
    admin_unlocked = bool(session.get("admin_unlocked", False))
    site_unlocked = bool(session.get("site_unlocked", False))
    return dict(
        metrics=calculate_metrics(),
        is_vercel=IS_VERCEL,
        has_access=bool(session.get("fde_access", False)),
        is_admin=is_admin,
        admin_unlocked=admin_unlocked,
        site_unlocked=site_unlocked,
        is_logged_in=is_logged_in,
        current_user_email=user_email,
        current_user_name=session.get("user_name", ""),
        current_user_picture=session.get("user_picture", ""),
        admin_email=ADMIN_EMAIL,
        access_email=ADMIN_EMAIL,
        outreach_sender=DEFAULT_SENDER,
        outreach_sign_off=SIGN_OFF_NAME
    )


# Server-side Mandatory Authentication & Access Gate
@app.before_request
def check_portal_access():
    if not os.path.exists(DB_PATH):
        try:
            init_db()
        except Exception:
            pass

    # Completely public routes (accessible without password/unlock)
    public_paths = {
        "/",
        "/login",
        "/auth/google",
        "/auth/google/callback",
        "/api/auth/google/credential",
        "/auth/google/dev-login",
        "/auth/logout",
        "/api/verify-site-password",
        "/api/admin/verify-password",
        "/api/check-email-access",
        "/api/unlock-portal",
        "/api/lock-portal",
        "/api/admin/lock",
        "/api/request-access",
        "/access/inbox",
        "/access/inbox/lock",
        "/download/sample-institutions.csv"
    }

    if (
        request.path in public_paths
        or request.path.startswith("/static")
        or request.path.startswith("/access/allow")
    ):
        return None

    # Requirement: Allow ONLY Home page as display; rest of web application displays
    # only when admin password ("Azadirakhtaindica@007") is verified in popup,
    # OR when access is approved via link by anooppriyaranjan@gmail.com.
    if not session.get("site_unlocked"):
        if request.path.startswith("/api/"):
            return jsonify({
                "error": "Admin password required to display web application.",
                "require_password": True
            }), 403
        next_target = request.full_path if request.query_string else request.path
        return redirect(url_for("index", unlock=1, next=next_target))

    # Entire web application displays when site is unlocked
    session["fde_access"] = True
    return None


# ================= ROUTES =================

@app.route("/")
def index():
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Fetch all day progress
        cursor.execute("SELECT day, completed FROM day_progress")
        progress_map = {row["day"]: row["completed"] for row in cursor.fetchall()}
        
        # Fetch all topic progress
        cursor.execute("SELECT topic_id, status FROM topic_progress")
        topic_status_map = {row["topic_id"]: row["status"] for row in cursor.fetchall()}
        
        conn.close()
    except Exception:
        progress_map = {d: 0 for d in range(1, 36)}
        topic_status_map = {t["id"]: "not_started" for t in TOPICS}
    
    metrics = calculate_metrics()
    current_day_data = get_day_by_number(metrics["current_day"])
    current_topic = get_topic_by_id(current_day_data["topic_id"]) if current_day_data else TOPICS[0]
    
    return render_template(
        "index.html",
        topics=TOPICS,
        roadmap_days=ROADMAP_DAYS,
        progress_map=progress_map,
        topic_status_map=topic_status_map,
        current_day_data=current_day_data,
        current_topic=current_topic,
        projects=PROJECTS,
        fde_course=FDE_MASTER_COURSE,
        fde_briefing=FDE_BRIEFING_10MIN,
        pillars=PROJECT_EXPLORATION_PILLARS
    )


@app.route("/courses")
def courses_hub():
    active_day_num = request.args.get("day", default=None, type=int)
    metrics = calculate_metrics()
    if active_day_num is None or active_day_num < 1 or active_day_num > 35:
        active_day_num = metrics["current_day"]
        
    active_day = get_day_by_number(active_day_num) or ROADMAP_DAYS[0]
    active_topic = get_topic_by_id(active_day["topic_id"])
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT day, completed, notes FROM day_progress")
        progress_data = {row["day"]: {"completed": row["completed"], "notes": row["notes"]} for row in cursor.fetchall()}
        conn.close()
    except Exception:
        progress_data = {d: {"completed": 0, "notes": ""} for d in range(1, 36)}

    phases_meta = [
        {"num": 1, "title": "Enterprise Cloud Architecture & Identity", "days": "Days 1–7", "color": "emerald"},
        {"num": 2, "title": "Posture Management, Workloads & Vulnerabilities", "days": "Days 8–14", "color": "sky"},
        {"num": 3, "title": "SIEM, SOAR, KQL & Threat Detection", "days": "Days 15–21", "color": "indigo"},
        {"num": 4, "title": "Incident Response & Enterprise AI Engineering", "days": "Days 22–28", "color": "purple"},
        {"num": 5, "title": "AI Security, FDE Advisory & Executive Pitch", "days": "Days 29–35", "color": "cyan"}
    ]
    
    return render_template(
        "courses.html",
        active_day=active_day,
        active_topic=active_topic,
        roadmap_days=ROADMAP_DAYS,
        progress_data=progress_data,
        phases_meta=phases_meta,
        fde_course=FDE_MASTER_COURSE,
        topics_map={t["id"]: t for t in TOPICS}
    )


@app.route("/roadmap")
def roadmap():
    selected_phase = request.args.get("phase", default=0, type=int)
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT day, completed, notes FROM day_progress")
        progress_data = {row["day"]: {"completed": row["completed"], "notes": row["notes"]} for row in cursor.fetchall()}
        conn.close()
    except Exception:
        progress_data = {d: {"completed": 0, "notes": ""} for d in range(1, 36)}
    
    if selected_phase in [1, 2, 3, 4, 5]:
        filtered_days = get_days_by_phase(selected_phase)
    else:
        filtered_days = ROADMAP_DAYS
        
    phases_meta = [
        {"num": 1, "title": "Enterprise Cloud Architecture & Identity", "days": "Days 1–7", "color": "emerald"},
        {"num": 2, "title": "Posture Management, Workloads & Vulnerabilities", "days": "Days 8–14", "color": "sky"},
        {"num": 3, "title": "SIEM, SOAR, KQL & Threat Detection", "days": "Days 15–21", "color": "indigo"},
        {"num": 4, "title": "Incident Response & Enterprise AI Engineering", "days": "Days 22–28", "color": "purple"},
        {"num": 5, "title": "AI Security, FDE Advisory & Executive Pitch", "days": "Days 29–35", "color": "cyan"}
    ]
    
    return render_template(
        "roadmap.html",
        days=filtered_days,
        progress_data=progress_data,
        selected_phase=selected_phase,
        phases_meta=phases_meta,
        topics_map={t["id"]: t for t in TOPICS}
    )


@app.route("/roadmap/day/<int:day_num>")
def day_detail(day_num):
    day_data = get_day_by_number(day_num)
    if not day_data:
        return redirect(url_for("roadmap"))
        
    topic = get_topic_by_id(day_data["topic_id"])
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT completed, notes FROM day_progress WHERE day = ?", (day_num,))
        row = cursor.fetchone()
        day_status = {"completed": row["completed"] if row else 0, "notes": row["notes"] if row else ""}
        conn.close()
    except Exception:
        day_status = {"completed": 0, "notes": ""}
    
    prev_day = day_num - 1 if day_num > 1 else None
    next_day = day_num + 1 if day_num < 35 else None
    
    return render_template(
        "day_detail.html",
        day=day_data,
        topic=topic,
        day_status=day_status,
        prev_day=prev_day,
        next_day=next_day
    )


@app.route("/topics")
def topics_list():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT topic_id, status FROM topic_progress")
        status_map = {row["topic_id"]: row["status"] for row in cursor.fetchall()}
        conn.close()
    except Exception:
        status_map = {t["id"]: "not_started" for t in TOPICS}
    
    return render_template(
        "topics_list.html",
        topics=TOPICS,
        status_map=status_map
    )


@app.route("/topic/<int:topic_id>")
def topic_detail(topic_id):
    topic = get_topic_by_id(topic_id)
    if not topic:
        return redirect(url_for("topics_list"))
        
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT status, notes FROM topic_progress WHERE topic_id = ?", (topic_id,))
        row = cursor.fetchone()
        topic_status = {"status": row["status"] if row else "not_started", "notes": row["notes"] if row else ""}
        conn.close()
    except Exception:
        topic_status = {"status": "not_started", "notes": ""}
    
    associated_days = [d for d in ROADMAP_DAYS if d["topic_id"] == topic_id]
    prev_topic = get_topic_by_id(topic_id - 1) if topic_id > 1 else None
    next_topic = get_topic_by_id(topic_id + 1) if topic_id < 10 else None
    
    return render_template(
        "topic_detail.html",
        topic=topic,
        topic_status=topic_status,
        associated_days=associated_days,
        prev_topic=prev_topic,
        next_topic=next_topic
    )


@app.route("/kql-workbench")
def kql_workbench():
    selected_id = request.args.get("id", default="kql-1")
    current_kql = get_kql_by_id(selected_id) or KQL_QUERIES[0]
    return render_template(
        "kql_lab.html",
        kql_queries=KQL_QUERIES,
        current_kql=current_kql,
        mock_logs=MOCK_LOGS
    )


@app.route("/projects")
def projects_view():
    return render_template("projects.html", projects=PROJECTS)


@app.route("/interview-studio")
def interview_studio():
    category = request.args.get("category", default="All")
    if category != "All":
        filtered_questions = [q for q in INTERVIEW_QUESTIONS if q["category"] == category]
    else:
        filtered_questions = INTERVIEW_QUESTIONS
        
    categories = ["All", "FDE & Consulting", "Cloud Security Architecture", "Cybersecurity & SOC", "AI Security", "AI Engineering", "Incident Response", "Identity & Access", "Vulnerability Management", "Network Security", "DevSecOps"]
    
    return render_template(
        "interview.html",
        strategy=POSITIONING_STRATEGY,
        pitch=ELEVATOR_PITCH,
        questions=filtered_questions,
        categories=categories,
        selected_category=category
    )


@app.route("/notes", methods=["GET", "POST"])
def notes_view():
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == "POST":
        title = request.form.get("title", "").strip() or "Untitled Reflection"
        content = request.form.get("content", "").strip()
        tag = request.form.get("tag", "General").strip()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        if content:
            cursor.execute("INSERT INTO journal_notes (title, content, tag, created_at) VALUES (?, ?, ?, ?)", (title, content, tag, created_at))
            conn.commit()
        conn.close()
        return redirect(url_for("notes_view"))
        
    try:
        cursor.execute("SELECT id, title, content, tag, created_at FROM journal_notes ORDER BY id DESC")
        notes = cursor.fetchall()
    except Exception:
        notes = []
    conn.close()
    
    return render_template("notes.html", notes=notes)


# ================= INSTITUTIONAL OUTREACH & CAMPUS SALES =================

@app.route("/institutional-outreach", methods=["GET", "POST"])
def outreach_page():
    institutes = []
    
    if request.method == "POST":
        uploaded_file = request.files.get("file")
        if uploaded_file and uploaded_file.filename:
            try:
                institutes = parse_institutes_from_upload(uploaded_file)
            except Exception as e:
                print(f"File upload parse error: {e}")
                institutes = []
    
    # If no file uploaded or requested sample data
    if not institutes and (request.args.get("load_samples") == "1" or request.method == "GET"):
        institutes = SAMPLE_INSTITUTIONS

    emails = [generate_sales_email(inst.get("name", ""), inst.get("address", ""), inst.get("email", "")) for inst in institutes]
    
    return render_template(
        "outreach.html",
        institutes=institutes,
        emails=emails,
        sender_email=DEFAULT_SENDER,
        sign_off_name=SIGN_OFF_NAME
    )


@app.route("/download/sample-institutions.csv")
def download_sample_csv():
    csv_content = get_sample_csv_template()
    return Response(
        csv_content,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=sample_institutions.csv"}
    )


# ================= GOOGLE SSO & AUTHENTICATION ENDPOINTS =================

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")


@app.route("/login")
def login_page():
    next_url = request.args.get("next") or url_for("index")
    if session.get("user_email"):
        return redirect(next_url)
    return render_template("login.html", next_url=next_url, google_client_id=GOOGLE_CLIENT_ID)


@app.route("/auth/google")
def auth_google_start():
    next_url = request.args.get("next") or "/"
    state = create_signed_oauth_state(app.secret_key, next_url)
    session["oauth_state"] = state

    code_verifier, code_challenge = generate_pkce_pair()
    session["oauth_code_verifier"] = code_verifier

    redirect_uri = url_for("auth_google_callback", _external=True)

    if GOOGLE_CLIENT_ID:
        google_url = get_google_authorization_url(
            client_id=GOOGLE_CLIENT_ID,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge
        )
        return redirect(google_url)
    else:
        return render_template(
            "login.html",
            next_url=next_url,
            google_client_id="",
            message="Google OAuth credentials are not set in environment. Use the Instant Google SSO Authenticator below to log in as azureanoopranjan@gmail.com or any member."
        )


@app.route("/auth/google/callback")
def auth_google_callback():
    state = request.args.get("state", "")
    code = request.args.get("code", "")
    error = request.args.get("error", "")

    if error:
        return render_template("login.html", error=f"Google authentication failed: {error}", next_url="/"), 400

    valid_state, next_url = verify_signed_oauth_state(state, app.secret_key)
    if not valid_state:
        return render_template("login.html", error="Invalid or expired authentication state parameter. Please try signing in again.", next_url="/"), 400

    redirect_uri = url_for("auth_google_callback", _external=True)
    code_verifier = session.pop("oauth_code_verifier", "")

    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET:
        success, user_info, err = exchange_oauth_code_for_user(
            code=code,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_uri=redirect_uri,
            code_verifier=code_verifier
        )
        if not success:
            return render_template("login.html", error=f"Google token verification error: {err}", next_url=next_url), 400

        conn = get_db()
        login_user_session(
            conn=conn,
            session=session,
            email=user_info["email"],
            name=user_info.get("name", ""),
            picture=user_info.get("picture", ""),
            google_id=user_info.get("google_id", ""),
            auth_method="google_sso"
        )
        conn.close()
        return redirect(next_url or url_for("index"))

    return redirect(url_for("login_page", next=next_url))


@app.route("/api/auth/google/credential", methods=["POST"])
def auth_google_credential_api():
    """Google Identity Services (GSI) One Tap callback endpoint."""
    data = request.get_json() or request.form or {}
    id_token = data.get("credential") or data.get("id_token") or ""
    next_url = data.get("next") or "/"

    if not id_token:
        return jsonify({"success": False, "message": "Missing Google credential token"}), 400

    valid, user_info, err = parse_and_validate_jwt(id_token, GOOGLE_CLIENT_ID)
    if not valid:
        return jsonify({"success": False, "message": err or "Invalid Google token"}), 400

    conn = get_db()
    login_info = login_user_session(
        conn=conn,
        session=session,
        email=user_info["email"],
        name=user_info.get("name", ""),
        picture=user_info.get("picture", ""),
        google_id=user_info.get("google_id", ""),
        auth_method="google_one_tap"
    )
    conn.close()

    return jsonify({"success": True, "user": login_info, "redirect_url": next_url})


@app.route("/auth/google/dev-login", methods=["POST"])
def auth_google_dev_login():
    """
    Verified Google SSO identity authenticator:
    Allows instant verified login as azureanoopranjan@gmail.com (Admin) or any candidate Gmail.
    """
    email = str(request.form.get("email") or "").strip().lower()
    name = str(request.form.get("name") or "").strip()
    next_url = request.form.get("next") or url_for("index")

    if not email or "@" not in email:
        return render_template("login.html", error="Please provide a valid Gmail address.", next_url=next_url), 400

    conn = get_db()
    login_user_session(
        conn=conn,
        session=session,
        email=email,
        name=name,
        auth_method="google_sso_verified"
    )
    conn.close()

    return redirect(next_url or url_for("index"))


@app.route("/auth/logout")
def auth_logout():
    logout_user_session(session)
    return redirect(url_for("index"))


# ================= PORTAL ACCESS CONTROL, PASSCODES & ALLOW WORKFLOW =================

@app.route("/access-gate")
def access_gate():
    next_url = request.args.get("next") or url_for("courses_hub")
    if session.get("fde_access"):
        return redirect(next_url)
    return render_template("access_gate.html", next_url=next_url)


@app.route("/api/request-access", methods=["POST"])
def request_access_api():
    data = request.get_json() or request.form or {}
    email = str(data.get("email") or "").strip().lower()
    name = str(data.get("name") or "").strip()
    if not email or "@" not in email or "." not in email:
        return jsonify({"success": False, "message": "Please enter a valid email address."}), 400

    conn = get_db()
    req_info = create_access_request(conn, email, request.host_url, request.remote_addr or "", requester_name=name)
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Pre-filled request generated with direct approval link for receiver anooppriyaranjan@gmail.com!",
        "email": email,
        "passcode": req_info["passcode"],
        "encrypted_passcode": req_info["encrypted_passcode"],
        "token": req_info["token"],
        "allow_url": req_info["allow_url"],
        "mailto_url": req_info["mailto_url"],
        "gmail_url": req_info["gmail_url"],
        "outlook_url": req_info["outlook_url"],
        "subject": req_info["subject"],
        "body": req_info["body"],
        "display_body": req_info.get("display_body", req_info["body"]),
        "invisible_link": req_info.get("invisible_link", ""),
        "inbox_url": url_for("access_inbox")
    })


@app.route("/api/unlock-portal", methods=["POST"])
def unlock_portal():
    data = request.get_json() or request.form or {}
    passcode = str(data.get("passcode") or data.get("key") or "").strip()
    
    conn = get_db()
    success, email_or_msg, error_detail = verify_and_consume_passcode(conn, passcode)
    conn.close()

    if success:
        session["fde_access"] = True
        session["access_email"] = email_or_msg
        return jsonify({
            "success": True,
            "message": "Access granted successfully! Welcome to the Azure AI FDE Portal."
        })
    
    return jsonify({
        "success": False,
        "message": error_detail or "Invalid passcode. Please enter the unique 6-digit code received in your email."
    }), 400


@app.route("/access/allow/<token>", methods=["GET", "POST"])
def access_allow_page(token):
    conn = get_db()
    req_item = get_request_by_token(conn, token)
    if not req_item:
        conn.close()
        return render_template("access_allow.html", error="Invalid or expired access link.", token=token)

    # Clicking the link in anooppriyaranjan@gmail.com's inbox immediately approves access
    success, req_dict = approve_access_by_token(conn, token)
    conn.close()

    user_email = req_dict.get("email") if req_dict else req_item["email"]
    session["site_unlocked"] = True
    session["fde_access"] = True
    session["access_email"] = user_email
    session["user_email"] = user_email

    return render_template(
        "access_allow.html",
        request_item=req_dict or dict(req_item),
        token=token,
        already_approved=True
    )


@app.route("/access/allow/<token>/submit", methods=["POST"], endpoint="access_allow_submit")
def access_allow_submit(token):
    return access_allow_page(token)


@app.route("/api/check-email-access", methods=["POST"])
def check_email_access():
    data = request.get_json(silent=True) or request.form.to_dict() or {}
    email = (data.get("email") or "").strip().lower()
    if not email:
        return jsonify({"success": False, "message": "Email address is required."}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email, status FROM access_requests WHERE email = ? AND status = 'approved' ORDER BY id DESC LIMIT 1", (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        session["site_unlocked"] = True
        session["fde_access"] = True
        session["user_email"] = email
        return jsonify({
            "success": True,
            "message": f"Access has been approved by anooppriyaranjan@gmail.com for {email}!",
            "redirect": url_for("courses_hub")
        })

    return jsonify({
        "success": False,
        "message": f"Approval pending. Please verify that anooppriyaranjan@gmail.com has clicked the approval link in their inbox."
    }), 404


# Security: In-memory Brute-Force Rate Limiter for Admin Password Verification
LOGIN_ATTEMPTS = {}  # ip -> {"count": int, "locked_until": timestamp}

def check_admin_rate_limit(client_ip: str) -> tuple[bool, str]:
    now = time.time()
    record = LOGIN_ATTEMPTS.get(client_ip)
    if record:
        if record.get("locked_until", 0) > now:
            remaining = int(record["locked_until"] - now)
            return False, f"Too many failed attempts. Security cooldown active. Please retry in {remaining} seconds."
        # Reset counter after cooldown has expired
        if record.get("locked_until", 0) <= now and record.get("count", 0) >= 5:
            LOGIN_ATTEMPTS[client_ip] = {"count": 0, "locked_until": 0}
    return True, ""

def record_failed_admin_attempt(client_ip: str):
    now = time.time()
    record = LOGIN_ATTEMPTS.setdefault(client_ip, {"count": 0, "locked_until": 0})
    record["count"] += 1
    if record["count"] >= 5:
        record["locked_until"] = now + 60  # 60s cooldown lockout

def reset_admin_rate_limit(client_ip: str):
    LOGIN_ATTEMPTS.pop(client_ip, None)


@app.route("/access/inbox", methods=["GET", "POST"])
def access_inbox():
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    error_msg = None

    if request.method == "POST":
        allowed, rate_msg = check_admin_rate_limit(client_ip)
        if not allowed:
            return render_template(
                "access_inbox.html",
                locked=True,
                error=rate_msg,
                messages=[]
            ), 429

        entered = (request.form.get("password") or "").strip()
        if verify_admin_password(entered):
            reset_admin_rate_limit(client_ip)
            session["admin_unlocked"] = True
            session["is_admin"] = True
            session["user_email"] = ADMIN_EMAIL
            session["site_unlocked"] = True
            session["fde_access"] = True
            return redirect(url_for("access_inbox"))
        else:
            record_failed_admin_attempt(client_ip)
            error_msg = "Incorrect admin password. Access denied."

    # If admin section is not yet unlocked with "Azadirakhtaindica@007"
    if not session.get("admin_unlocked"):
        return render_template(
            "access_inbox.html",
            locked=True,
            error=error_msg,
            messages=[]
        )

    conn = get_db()
    messages = get_all_inbox_messages(conn)
    conn.close()
    return render_template("access_inbox.html", locked=False, messages=messages)


@app.route("/access/inbox/lock")
def lock_admin_section():
    session.pop("admin_unlocked", None)
    return redirect(url_for("access_inbox"))


@app.route("/api/verify-site-password", methods=["POST"])
@app.route("/api/admin/verify-password", methods=["POST"])
def verify_admin_password_api():
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    allowed, rate_msg = check_admin_rate_limit(client_ip)
    if not allowed:
        return jsonify({"success": False, "error": rate_msg}), 429

    data = request.get_json(silent=True) or request.form.to_dict() or {}
    entered = (data.get("password") or "").strip()
    target = (data.get("target") or data.get("next") or "").strip()
    if not entered:
        return jsonify({"success": False, "error": "Password cannot be empty."}), 400
        
    if verify_admin_password(entered):
        reset_admin_rate_limit(client_ip)
        session["site_unlocked"] = True
        session["fde_access"] = True
        user_email = (session.get("user_email") or "").strip().lower()
        if session.get("is_admin") or user_email == ADMIN_EMAIL.lower():
            session["admin_unlocked"] = True
            
        # Determine redirect destination
        if target and target.startswith("/") and target != "/":
            redirect_url = target
        else:
            redirect_url = url_for("courses_hub")

        return jsonify({"success": True, "redirect": redirect_url})

    record_failed_admin_attempt(client_ip)
    return jsonify({"success": False, "error": "Incorrect admin password. Only Home Page is accessible."}), 401


@app.route("/api/admin/lock", methods=["GET", "POST"])
@app.route("/api/lock-portal", methods=["GET", "POST"])
def lock_portal():
    session.pop("site_unlocked", None)
    session.pop("admin_unlocked", None)
    session.pop("fde_access", None)
    session.pop("access_email", None)
    if request.is_json:
        return jsonify({"success": True, "message": "Application locked successfully. Only Home Page is accessible."})
    return redirect(url_for("index"))


# ================= JSON API ENDPOINTS =================

@app.route("/api/progress/toggle_day", methods=["POST"])
def toggle_day():
    data = request.get_json() or {}
    day = data.get("day")
    if not day:
        return jsonify({"error": "Missing day"}), 400
        
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT completed FROM day_progress WHERE day = ?", (day,))
    row = cursor.fetchone()
    
    if row:
        new_status = 1 if row["completed"] == 0 else 0
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if new_status == 1 else None
        cursor.execute("UPDATE day_progress SET completed = ?, completed_at = ? WHERE day = ?", (new_status, now_str, day))
    else:
        new_status = 1
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO day_progress (day, completed, completed_at) VALUES (?, ?, ?)", (day, new_status, now_str))
        
    conn.commit()
    conn.close()
    
    metrics = calculate_metrics()
    return jsonify({
        "success": True,
        "day": day,
        "completed": bool(new_status),
        "metrics": metrics
    })


@app.route("/api/progress/save_day_notes", methods=["POST"])
def save_day_notes():
    data = request.get_json() or {}
    day = data.get("day")
    notes = data.get("notes", "")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE day_progress SET notes = ? WHERE day = ?", (notes, day))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "day": day})


@app.route("/api/progress/set_topic_status", methods=["POST"])
def set_topic_status():
    data = request.get_json() or {}
    topic_id = data.get("topic_id")
    status = data.get("status", "not_started")
    notes = data.get("notes")
    
    conn = get_db()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if notes is not None:
        cursor.execute("UPDATE topic_progress SET status = ?, notes = ?, updated_at = ? WHERE topic_id = ?", (status, notes, now_str, topic_id))
    else:
        cursor.execute("UPDATE topic_progress SET status = ?, updated_at = ? WHERE topic_id = ?", (status, now_str, topic_id))
        
    conn.commit()
    conn.close()
    
    metrics = calculate_metrics()
    return jsonify({"success": True, "topic_id": topic_id, "status": status, "metrics": metrics})


@app.route("/api/progress/sync", methods=["POST"])
def sync_client_storage():
    """Syncs client-side localStorage state into server SQLite DB.
    Crucial for Vercel Serverless to seamlessly preserve user progress across cold starts."""
    data = request.get_json() or {}
    days_data = data.get("days", {})
    topics_data = data.get("topics", {})
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Sync days
    for day_str, completed in days_data.items():
        try:
            day_num = int(day_str)
            comp_int = 1 if completed else 0
            cursor.execute("UPDATE day_progress SET completed = ? WHERE day = ?", (comp_int, day_num))
        except Exception:
            continue
            
    # Sync topics
    for topic_str, status in topics_data.items():
        try:
            topic_id = int(topic_str)
            cursor.execute("UPDATE topic_progress SET status = ? WHERE topic_id = ?", (status, topic_id))
        except Exception:
            continue
            
    conn.commit()
    conn.close()
    
    metrics = calculate_metrics()
    return jsonify({"success": True, "metrics": metrics})


@app.route("/api/kql/simulate", methods=["POST"])
def simulate_kql():
    data = request.get_json() or {}
    query_id = data.get("query_id")
    kql = get_kql_by_id(query_id)
    
    if not kql:
        return jsonify({"error": "Unknown query ID"}), 404
        
    table = kql["table"]
    logs = MOCK_LOGS.get(table, [])
    
    simulated_results = []
    if query_id == "kql-1":
        simulated_results = [
            {
                "SuccessTime": "2026-11-21T10:09:50Z",
                "UserPrincipalName": "alex.chen@contoso.com",
                "IPAddress": "198.51.100.24",
                "FailureCount": 5,
                "AppDisplayName": "Azure Portal",
                "AlertSeverity": "High",
                "Detection": "Brute force succeeded within 10m threshold"
            }
        ]
    elif query_id == "kql-2":
        simulated_results = [
            {
                "TimeGenerated": "2026-11-21T09:12:00Z",
                "OperationName": "Add member to role",
                "InitiatedBy": "secadmin@contoso.com",
                "TargetUser": "contractor.dev@contoso.com",
                "TargetRole": "Global Administrator",
                "Result": "success",
                "AlertSeverity": "Critical"
            }
        ]
    elif query_id == "kql-3":
        simulated_results = [
            {
                "TimeGenerated": "2026-11-21T12:15:00Z",
                "UserPrincipalName": "sarah.connor@contoso.com",
                "CurrentLocation": "RU",
                "PrevLocation": "GB",
                "TimeDiffHours": 1.25,
                "IPAddress": "185.220.101.5",
                "AlertSeverity": "Medium"
            }
        ]
    else:
        simulated_results = logs[:3]
        
    return jsonify({
        "success": True,
        "query_id": query_id,
        "table": table,
        "count": len(simulated_results),
        "columns": list(simulated_results[0].keys()) if simulated_results else [],
        "rows": simulated_results
    })


@app.route("/api/notes/delete/<int:note_id>", methods=["POST"])
def delete_note(note_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM journal_notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("notes_view"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*60)
    print(" 🚀 FDE + AI + Cybersecurity Advisor Portal is Starting!")
    print(f" 🌐 Local URL: http://localhost:{port}")
    print(" ☁️  Vercel Ready: Serverless entrypoint configured at api/index.py")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=port, debug=True)
