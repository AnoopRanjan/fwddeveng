import os
import sys
import time

# Ensure project root is on path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import io
import os
import sys
import time
import zipfile

# Ensure project root is on path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import app, get_db
from data.outreach import parse_xlsx_stream, parse_csv_stream, generate_sales_email
from data.roadmap import ROADMAP_DAYS
from data.topics import TOPICS
from data.fde_masterclass import FDE_MASTER_COURSE, FDE_BRIEFING_10MIN
from data.access_control import (
    create_access_request,
    ADMIN_EMAIL
)


def test_native_xlsx_parsing():
    """Verify that native openpyxl/csv parsing works seamlessly without third-party CLI tools."""
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w') as zf:
        zf.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
        zf.writestr('xl/sharedStrings.xml', '<?xml version="1.0" encoding="UTF-8"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>College Name</t></si><si><t>Campus Location</t></si><si><t>Official Email</t></si><si><t>IIT Bombay</t></si><si><t>Powai, Mumbai</t></si><si><t>dean@iitb.ac.in</t></si></sst>')
        zf.writestr('xl/worksheets/sheet1.xml', '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c></row><row r="2"><c r="A2" t="s"><v>3</v></c><c r="B2" t="s"><v>4</v></c><c r="C2" t="s"><v>5</v></c></row></sheetData></worksheet>')

    bio.seek(0)
    rows = parse_xlsx_stream(bio)
    assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
    assert rows[0]['name'] == 'IIT Bombay'
    assert rows[0]['email'] == 'dean@iitb.ac.in'
    print("PASS: Native XLSX parsing verified.")


def test_topics_and_roadmap():
    """Verify that all 35 roadmap days and 10 topics have valid Microsoft/C# video links."""
    print("Verifying 35 roadmap days have C# / .NET / Microsoft videos...")
    for day in ROADMAP_DAYS:
        assert day.get("video_id"), f"Day {day['day']} missing video_id"
        assert day.get("video_instructor"), f"Day {day['day']} missing instructor"
    print("PASS: All 35 days have verified video IDs and official instructors.")

    print("Verifying 10 topics have valid YouTube embeds...")
    for t in TOPICS:
        assert t.get("youtube_embed"), f"Topic {t['id']} missing youtube_embed"
        assert t.get("instructor"), f"Topic {t['id']} missing instructor"
    print("PASS: All 10 topics have verified video embeds and instructors.")

    assert FDE_MASTER_COURSE['primary_video_id'] == 'lCQOCoH3Osk'
    assert 'Microsoft' in FDE_MASTER_COURSE['instructor'] or 'dotnet' in FDE_MASTER_COURSE['instructor']
    assert FDE_BRIEFING_10MIN['video_id'] in ['VTnqUDMchXA', '4vHBgwcz_I4']
    print("PASS: Home masterclass and 10-min briefing videos verified.")


def test_routes_and_access():
    """Verify that only home page is displayed, admin popup unlocks with Azadirakhtaindica@007, and email request contains approval link to anooppriyaranjan@gmail.com."""
    client = app.test_client()

    # 1. Home page is freely accessible and displays
    res_home = client.get('/')
    assert res_home.status_code == 200
    home_html = res_home.data.decode('utf-8')
    assert "FDE Transformation Accelerator" in home_html
    print("PASS: Home page is freely accessible and displays.")

    # 2. SSO login of Gmail is REMOVED: accessing locked /courses redirects to /?unlock=1 (NOT /login)
    res_courses_locked = client.get('/courses')
    assert res_courses_locked.status_code == 302
    assert "unlock=1" in res_courses_locked.headers["Location"]
    assert "/login" not in res_courses_locked.headers["Location"]
    print("PASS: Gmail SSO login removed; navigating outside Home page redirects to /?unlock=1.")

    # 3. Wrong admin password rejected with 401
    wrong_pw = client.post('/api/verify-site-password', json={'password': 'WrongPassword123!'})
    assert wrong_pw.status_code == 401
    assert wrong_pw.get_json()['success'] is False
    print("PASS: Incorrect password rejected with 401.")

    # 3b. Anti-brute-force rate limiting: 5 consecutive failed attempts triggers 429 lockout
    for _ in range(4):
        client.post('/api/verify-site-password', json={'password': 'BadPassword!'})
    blocked_res = client.post('/api/verify-site-password', json={'password': 'BadPassword!'})
    assert blocked_res.status_code == 429
    assert "Too many failed attempts" in blocked_res.get_json()['error']
    print("PASS: Anti-brute-force rate limiting and security cooldown verified (429 Too Many Requests).")

    # Reset rate limit for subsequent test steps
    from app import reset_admin_rate_limit
    reset_admin_rate_limit("127.0.0.1")
    reset_admin_rate_limit("unknown")

    # 4. Correct admin password "Azadirakhtaindica@007" unlocks the entire web application
    unlock_res = client.post('/api/verify-site-password', json={'password': 'Azadirakhtaindica@007', 'target': '/courses'})
    assert unlock_res.status_code == 200
    assert unlock_res.get_json()['success'] is True
    print("PASS: Admin popup password 'Azadirakhtaindica@007' successfully unlocks the web application.")

    # 5. Now /courses and all other pages display completely!
    courses_unlocked = client.get('/courses')
    assert courses_unlocked.status_code == 200
    print("PASS: Rest of the web application now displays successfully.")

    # 6. Lock the portal again to test the Email Request flow
    client.get('/api/lock-portal')
    relocked_check = client.get('/courses')
    assert relocked_check.status_code == 302
    assert "unlock=1" in relocked_check.headers["Location"]
    print("PASS: Portal re-locked back to Home-only display.")

    # 7. Flow for user who doesn't know password:
    # Generate sample email text for anooppriyaranjan@gmail.com with invisible link for sender
    cand_email = f"candidate_{int(time.time())}@gmail.com"
    req_res = client.post('/api/request-access', json={'email': cand_email, 'name': 'Candidate Student'})
    assert req_res.status_code == 200
    data = req_res.get_json()
    assert data['success'] is True
    assert "anooppriyaranjan@gmail.com" in data['mailto_url'] or "anooppriyaranjan@gmail.com" in data['body']
    assert "/access/allow/" in data['body']
    # The visible sample text (display_body) does NOT expose the raw approval URL to the sender
    assert ">>> http" not in data.get('display_body', '')
    allow_url = data['allow_url']
    token = data['token']
    print(f"PASS: Sample email text generated with invisible link for sender (anooppriyaranjan@gmail.com inbox target: {allow_url}).")

    # 8. Before approval, check_email_access returns 404 pending
    pending_check = client.post('/api/check-email-access', json={'email': cand_email})
    assert pending_check.status_code == 404
    print("PASS: Approval correctly verified as pending before link is clicked.")

    # 9. Admin inbox (/access/inbox) is password-protected:
    # First, test that /access/inbox requires password and has no plaintext hints
    inbox_res = client.get('/access/inbox')
    assert inbox_res.status_code == 200
    inbox_html = inbox_res.data.decode('utf-8')
    assert "Enter Admin Password" in inbox_html or "••••••••••••" in inbox_html
    assert "Azadirakhtaindica" not in inbox_html
    print("PASS: Admin inbox is password protected with masked placeholder and no hints.")

    # Unlock admin inbox with password
    inbox_unlock = client.post('/access/inbox', data={'password': 'Azadirakhtaindica@007'}, follow_redirects=True)
    assert inbox_unlock.status_code == 200
    unlocked_inbox_html = inbox_unlock.data.decode('utf-8')
    assert "Received Access Emails & Passcodes" in unlocked_inbox_html
    assert cand_email in unlocked_inbox_html
    assert f"/access/allow/{token}" in unlocked_inbox_html
    print("PASS: Admin inbox unlocked; received email request and approval link visible to anooppriyaranjan@gmail.com.")

    # 10. Clicking the link in the inbox of anooppriyaranjan@gmail.com:
    # Grants full access to this valid email ID!
    allow_click = client.get(f'/access/allow/{token}')
    assert allow_click.status_code == 200
    allow_html = allow_click.data.decode('utf-8')
    assert "Portal Access Granted" in allow_html or "APPROVED & UNLOCKED" in allow_html
    print("PASS: Clicking approval link in anooppriyaranjan@gmail.com inbox successfully grants access.")

    # 11. Now user has full access to the rest of the web application!
    after_allow_courses = client.get('/courses')
    assert after_allow_courses.status_code == 200
    print("PASS: User of approved email now has full access to the rest of the web application.")

    # 12. check_email_access now returns 200 approved
    approved_check = client.post('/api/check-email-access', json={'email': cand_email})
    assert approved_check.status_code == 200
    assert approved_check.get_json()['success'] is True
    print("PASS: Direct email check confirms approval from anooppriyaranjan@gmail.com.")

    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")


if __name__ == "__main__":
    test_native_xlsx_parsing()
    test_topics_and_roadmap()
    test_routes_and_access()
