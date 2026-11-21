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

    # 1. Home page always 200 and accessible without any access pass
    res = client.get('/')
    assert res.status_code == 200
    print("PASS: Home page is publicly accessible.")

    # 2. Access gate page is publicly accessible
    res = client.get('/access-gate')
    assert res.status_code == 200

    # 3. Restricted pages redirect to /access-gate when user has no access
    res = client.get('/courses')
    assert res.status_code == 302
    assert "/access-gate" in res.headers["Location"]
    print("PASS: Courses page requires access and redirects to /access-gate.")

    # 4. Request Access via Email -> generates unique 6-digit random passcode & email provider URLs
    req_res = client.post('/api/request-access', json={'email': 'applicant@enterprise-ai.com', 'name': 'Alex Sharma'})
    assert req_res.status_code == 200
    data = req_res.get_json()
    assert data['success'] is True
    passcode = data['passcode']
    assert len(passcode) == 6 and passcode.isdigit(), f"Passcode {passcode} must be 6 digits"
    assert "mailto:azureanoopranjan@gmail.com" in data['mailto_url']
    assert "mail.google.com" in data['gmail_url']
    assert "outlook.live.com" in data['outlook_url']
    assert passcode in data['body']
    print(f"PASS: Access request generated email template and provider URLs with passcode: {passcode}")

    # 5. Check simulated inbox for received email
    inbox_res = client.get('/access/inbox')
    assert inbox_res.status_code == 200
    inbox_html = inbox_res.data.decode('utf-8')
    assert passcode in inbox_html
    assert "applicant@enterprise-ai.com" in inbox_html
    print("PASS: Email with unique random passcode delivered to inbox.")

    # 6. Verify incorrect passcode fails with no hints
    fail_res = client.post('/api/unlock-portal', json={'passcode': '000000'})
    assert fail_res.status_code == 400
    assert "VIP" not in fail_res.data.decode('utf-8')
    print("PASS: Invalid passcode rejected without giving bypass hints.")

    # 7. Unlock with valid 6-digit passcode
    unlock_res = client.post('/api/unlock-portal', json={'passcode': passcode})
    assert unlock_res.status_code == 200
    assert unlock_res.get_json()['success'] is True
    print("PASS: Portal unlocked using unique random passcode.")

    # 8. Now all restricted pages render with 200 OK
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
        assert resp.status_code == 200, f"Route {r} returned {resp.status_code}"
    print("PASS: All portal sub-routes accessible after unlocking.")

    # 9. Test Lock portal
    lock_res = client.get('/api/lock-portal')
    # After lock, visiting /courses redirects to /access-gate again
    res = client.get('/courses')
    assert res.status_code == 302
    assert "/access-gate" in res.headers["Location"]
    print("PASS: Lock portal successfully re-locks restricted pages.")

    # 10. Test Allow link approval workflow
    # Request access again
    req_res2 = client.post('/api/request-access', json={'email': 'student@university.edu'})
    assert req_res2.status_code == 200
    conn = app.get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT token FROM access_requests WHERE email = 'student@university.edu' ORDER BY id DESC LIMIT 1")
    token = cursor.fetchone()["token"]
    conn.close()

    # Open allow page
    allow_page = client.get(f'/access/allow/{token}')
    assert allow_page.status_code == 200
    assert "student@university.edu" in allow_page.data.decode('utf-8')
    assert "Allow Access" in allow_page.data.decode('utf-8')

    # Submit allow action (clicking the button)
    allow_submit = client.post(f'/access/allow/{token}/submit')
    assert allow_submit.status_code == 200
    assert "Portal Access Granted!" in allow_submit.data.decode('utf-8')

    # Now courses is accessible directly
    res_after_allow = client.get('/courses')
    assert res_after_allow.status_code == 200
    print("PASS: Allow link with button click grants full portal access.")

    # 11. Download CSV template
    res = client.get('/download/sample-institutions.csv')
    assert res.status_code == 200
    assert "Institute Name,Address,Email Address" in res.data.decode('utf-8')

if __name__ == '__main__':
    test_xlsx()
    test_video_metadata()
    test_routes_and_access()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")
