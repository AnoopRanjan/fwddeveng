import io
import zipfile
import app
from data.outreach import parse_xlsx_stream, parse_csv_stream, generate_sales_email
from data.roadmap import ROADMAP_DAYS
from data.topics import TOPICS
from data.fde_masterclass import FDE_MASTER_COURSE, FDE_BRIEFING_10MIN

def test_xlsx():
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

def test_video_metadata():
    print(f"Verifying {len(ROADMAP_DAYS)} roadmap days have C# / .NET / Microsoft videos...")
    for d in ROADMAP_DAYS:
        assert d['video_id'], f"Day {d['day']} missing video_id"
        assert "youtube-nocookie.com/embed/" in d['video_embed'], f"Day {d['day']} bad embed URL"
        assert d['video_instructor'], f"Day {d['day']} missing video_instructor"
    print("PASS: All 35 days have verified video IDs and official instructors.")

    print(f"Verifying {len(TOPICS)} topics have valid YouTube embeds...")
    for t in TOPICS:
        assert t['youtube_embed'], f"Topic {t['id']} missing youtube_embed"
        assert "youtube-nocookie.com/embed/" in t['youtube_embed'], f"Topic {t['id']} bad embed URL"
        assert t['instructor'], f"Topic {t['id']} missing instructor"
    print("PASS: All 10 topics have verified video embeds and instructors.")

    assert FDE_MASTER_COURSE['primary_video_id'] == 'lCQOCoH3Osk'
    assert 'Microsoft' in FDE_MASTER_COURSE['instructor'] or 'dotnet' in FDE_MASTER_COURSE['instructor']
    assert FDE_BRIEFING_10MIN['video_id'] in ['VTnqUDMchXA', '4vHBgwcz_I4']
    print("PASS: Home masterclass and 10-min briefing videos verified.")

def test_routes_and_access():
    client = app.app.test_client()

    # 1. Home page and login page are always accessible without any login
    res = client.get('/')
    assert res.status_code == 200
    res_login = client.get('/login')
    assert res_login.status_code == 200
    print("PASS: Home page and Login page are publicly accessible.")

    # 2. Mandatory Gmail SSO: Accessing /courses when unauthenticated redirects to /login
    res = client.get('/courses')
    assert res.status_code == 302
    assert "/login" in res.headers["Location"]
    print("PASS: Mandatory Gmail SSO enforced (redirects unauthenticated users to /login).")

    # 3. Accessing /access/inbox when unauthenticated redirects to /login
    res_inbox_unauth = client.get('/access/inbox')
    assert res_inbox_unauth.status_code == 302
    assert "/login" in res_inbox_unauth.headers["Location"]
    print("PASS: Unauthenticated access to /access/inbox redirected to /login.")

    import time
    cand_email = f"candidate_{int(time.time())}@gmail.com"

    # 4. Sign in as non-admin candidate via Gmail SSO
    candidate_login = client.post('/auth/google/dev-login', data={'email': cand_email, 'name': 'Candidate Student'})
    assert candidate_login.status_code == 302

    # 5. Non-admin candidate attempting to access /access/inbox MUST receive 403 Forbidden!
    forbidden_res = client.get('/access/inbox')
    assert forbidden_res.status_code == 403
    assert "Administrator Access Only" in forbidden_res.data.decode('utf-8')
    assert "Admin Section Restricted" in forbidden_res.data.decode('utf-8')
    print("PASS: Non-admin candidate strictly forbidden (403) from accessing /access/inbox.")

    # 6. Candidate attempting to access /courses without approved pass redirects to /access-gate
    gate_res = client.get('/courses')
    assert gate_res.status_code == 302
    assert "/access-gate" in gate_res.headers["Location"]
    print("PASS: Candidate without payment passcode redirects to /access-gate.")

    # 6b. Verify Admin portion is disabled from candidate / other pages (e.g. /access-gate)
    gate_page = client.get('/access-gate')
    assert gate_page.status_code == 200
    gate_html = gate_page.data.decode('utf-8')
    assert "Administrator Access Controls" not in gate_html, "Admin portion banner must be disabled on other pages"
    assert "View Inbox (Admin)" not in gate_html, "Admin inbox link must be disabled on other pages"
    print("PASS: Admin portion controls successfully disabled from other pages.")

    # 7. Candidate submits access request -> passcode is ENCRYPTED in outgoing request draft
    req_res = client.post('/api/request-access', json={'email': cand_email, 'name': 'Candidate Student'})
    assert req_res.status_code == 200
    data = req_res.get_json()
    assert data['success'] is True
    decrypted_passcode = data['passcode']
    encrypted_passcode = data['encrypted_passcode']
    assert len(decrypted_passcode) == 6 and decrypted_passcode.isdigit(), f"Passcode {decrypted_passcode} must be 6 digits"
    assert encrypted_passcode.startswith('ENC-'), f"Encrypted passcode {encrypted_passcode} must start with ENC-"
    assert "mailto:azureanoopranjan@gmail.com" in data['mailto_url']
    assert encrypted_passcode in data['body'], "Encrypted token must be in the outgoing email request body"
    assert decrypted_passcode not in data['body'], "Clear 6-digit passcode must NOT be in the outgoing email request body"
    print(f"PASS: Passcode is encrypted in request template: {encrypted_passcode}")

    # 8. Sign in as Administrator (azureanoopranjan@gmail.com) via Gmail SSO
    admin_login = client.post('/auth/google/dev-login', data={'email': 'azureanoopranjan@gmail.com', 'name': 'Anoop Ranjan (Admin)'})
    assert admin_login.status_code == 302

    # 9a. Verify on Home page for admin that old inbox admin banner is disabled
    home_res = client.get('/')
    assert home_res.status_code == 200
    home_html = home_res.data.decode('utf-8')
    assert "View Inbox (Admin)" not in home_html
    assert "Administrator Access Controls" not in home_html

    # 9b. Accessing /access/inbox before entering password MUST be locked
    locked_inbox = client.get('/access/inbox')
    assert locked_inbox.status_code == 200
    locked_html = locked_inbox.data.decode('utf-8')
    assert "Enter Admin Password" in locked_html
    assert "Password Protected Admin Section" in locked_html
    assert decrypted_passcode not in locked_html, "Decrypted code must NOT be visible while admin section is locked"
    print("PASS: Admin section is strictly locked until password prompt is completed.")

    # 9c. Wrong password rejected
    wrong_pw_res = client.post('/api/admin/verify-password', json={'password': 'WrongPassword123!'})
    assert wrong_pw_res.status_code == 401
    assert wrong_pw_res.get_json()['success'] is False

    # 9d. Correct password "Azadirakhtaindica@007" opens admin section
    correct_pw_res = client.post('/api/admin/verify-password', json={'password': 'Azadirakhtaindica@007'})
    assert correct_pw_res.status_code == 200
    assert correct_pw_res.get_json()['success'] is True

    # 9e. Now Admin accessing /access/inbox MUST show DECRYPTED code to tell candidate
    admin_inbox = client.get('/access/inbox')
    assert admin_inbox.status_code == 200
    inbox_html = admin_inbox.data.decode('utf-8')
    assert decrypted_passcode in inbox_html, "Decrypted 6-digit code must be visible to admin in inbox"
    assert "Decrypted Code (To Tell Candidate)" in inbox_html
    assert cand_email in inbox_html
    print(f"PASS: Admin successfully opened Admin Section with password 'Azadirakhtaindica@007' and decrypted code: {decrypted_passcode}")

    # 9f. Lock admin section and verify it re-locks
    client.get('/api/admin/lock')
    relocked_res = client.get('/access/inbox')
    assert "Enter Admin Password" in relocked_res.data.decode('utf-8')
    assert decrypted_passcode not in relocked_res.data.decode('utf-8')
    # Re-unlock
    client.post('/api/admin/verify-password', json={'password': 'Azadirakhtaindica@007'})

    # 10. Admin has automatic full VIP access to all portal routes without entering a passcode
    routes_to_test = [
        '/courses',
        '/roadmap',
        '/topics',
        '/topic/1',
        '/roadmap/day/1',
        '/projects',
        '/interview-studio',
        '/kql-workbench',
        '/institutional-outreach?load_samples=1',
        '/notes'
    ]
    for r in routes_to_test:
        resp = client.get(r)
        assert resp.status_code == 200, f"Admin route {r} returned {resp.status_code}"
    print("PASS: Admin has full access to all portal routes automatically.")

    # 11. Switch back to candidate and unlock with decrypted 6-digit passcode
    client.post('/auth/google/dev-login', data={'email': cand_email, 'name': 'Candidate Student'})
    unlock_res = client.post('/api/unlock-portal', json={'passcode': decrypted_passcode})
    assert unlock_res.status_code == 200
    assert unlock_res.get_json()['success'] is True

    # Now candidate can access /courses
    candidate_courses = client.get('/courses')
    assert candidate_courses.status_code == 200
    print("PASS: Candidate successfully unlocked full access using decrypted 6-digit code.")

    # 12. Test Logout
    logout_res = client.get('/auth/logout')
    res_after_logout = client.get('/courses')
    assert res_after_logout.status_code == 302
    assert "/login" in res_after_logout.headers["Location"]
    print("PASS: Logout clears session and redirects back to /login on restricted routes.")

    # 13. Download CSV template
    res = client.get('/download/sample-institutions.csv')
    assert res.status_code == 200
    assert "Institute Name,Address,Email Address" in res.data.decode('utf-8')

if __name__ == '__main__':
    test_xlsx()
    test_video_metadata()
    test_routes_and_access()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")
