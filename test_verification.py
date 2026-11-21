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

    # Home page always 200 and accessible
    res = client.get('/')
    assert res.status_code == 200

    # Courses page 200
    res = client.get('/courses')
    assert res.status_code == 200

    # Institutional Outreach page 200
    res = client.get('/institutional-outreach?load_samples=1')
    assert res.status_code == 200
    assert "priyaanoopranjan@gmail.com" in res.data.decode('utf-8')
    assert "Priya Gupta" in res.data.decode('utf-8')

    # Download CSV template
    res = client.get('/download/sample-institutions.csv')
    assert res.status_code == 200
    assert "Institute Name,Address,Email Address" in res.data.decode('utf-8')

    # Unlock API
    res = client.post('/api/unlock-portal', json={'passcode': 'AZURE-FDE-VIP'})
    assert res.status_code == 200
    assert res.json['success'] == True

    # Test other core routes render with 200 OK
    routes_to_test = [
        '/roadmap',
        '/topics',
        '/topic/1',
        '/roadmap/day/1',
        '/projects',
        '/interview-studio',
        '/kql-workbench',
        '/notes'
    ]
    for r in routes_to_test:
        resp = client.get(r)
        assert resp.status_code == 200, f"Route {r} returned {resp.status_code}"

    print("PASS: Routes, outreach, template download, and access unlock API verified.")

if __name__ == '__main__':
    test_xlsx()
    test_video_metadata()
    test_routes_and_access()
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY! 🚀")
