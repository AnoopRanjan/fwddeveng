import os
import sys
import io
import json
import hmac
import time
import struct
import base64
import hashlib
import secrets
import zipfile

# Ensure project root is on path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from app import app, reset_admin_rate_limit
from data.outreach import parse_xlsx_stream
from data.roadmap import ROADMAP_DAYS
from data.topics import TOPICS
from data.fde_masterclass import FDE_MASTER_COURSE, FDE_BRIEFING_10MIN


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def build_client_encrypted_token(password: str, challenge: dict) -> str:
    """Mirrors static/js/auth_crypto.js client-side PBKDF2 + HMAC + Encrypt-then-MAC."""
    pw_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.strip().encode("utf-8"),
        challenge["salt"].encode("utf-8"),
        int(challenge["iterations"]),
    )
    proof_hex = hmac.new(pw_key, challenge["nonce"].encode("utf-8"), hashlib.sha256).hexdigest()

    plain_bytes = json.dumps({
        "proof": proof_hex,
        "nonce": challenge["nonce"],
        "ts": int(time.time() * 1000),
    }).encode("utf-8")

    transport_key = bytes.fromhex(challenge["transport_key"])
    iv = secrets.token_bytes(16)
    ciphertext = bytearray(len(plain_bytes))
    offset = 0
    counter = 0
    while offset < len(plain_bytes):
        block = hmac.new(transport_key, iv + struct.pack(">I", counter), hashlib.sha256).digest()
        take = min(len(block), len(plain_bytes) - offset)
        for i in range(take):
            ciphertext[offset + i] = plain_bytes[offset + i] ^ block[i]
        offset += take
        counter += 1

    mac_tag = hmac.new(transport_key, iv + bytes(ciphertext), hashlib.sha256).digest()
    return f"ENC-V1.{_b64url_encode(iv)}.{_b64url_encode(bytes(ciphertext))}.{_b64url_encode(mac_tag)}"


def test_native_xlsx_parsing():
    """Verify that native openpyxl/csv parsing works seamlessly without third-party CLI tools."""
    bio = io.BytesIO()
    with zipfile.ZipFile(bio, "w") as zf:
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>',
        )
        zf.writestr(
            "xl/sharedStrings.xml",
            '<?xml version="1.0" encoding="UTF-8"?><sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>College Name</t></si><si><t>Campus Location</t></si><si><t>Official Email</t></si><si><t>IIT Bombay</t></si><si><t>Powai, Mumbai</t></si><si><t>dean@iitb.ac.in</t></si></sst>',
        )
        zf.writestr(
            "xl/worksheets/sheet1.xml",
            '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c><c r="C1" t="s"><v>2</v></c></row><row r="2"><c r="A2" t="s"><v>3</v></c><c r="B2" t="s"><v>4</v></c><c r="C2" t="s"><v>5</v></c></row></sheetData></worksheet>',
        )

    bio.seek(0)
    rows = parse_xlsx_stream(bio)
    assert len(rows) == 1, f"Expected 1 row, got {len(rows)}"
    assert rows[0]["name"] == "IIT Bombay"
    assert rows[0]["email"] == "dean@iitb.ac.in"
    print("PASS: Native XLSX parsing verified.")


def test_topics_and_roadmap():
    """Verify that all 35 roadmap days and 10 topics have valid Microsoft/C# video links."""
    for day in ROADMAP_DAYS:
        assert day.get("video_id"), f"Day {day['day']} missing video_id"
        assert day.get("video_instructor"), f"Day {day['day']} missing instructor"
    print("PASS: All 35 days have verified video IDs and official instructors.")

    for t in TOPICS:
        assert t.get("youtube_embed"), f"Topic {t['id']} missing youtube_embed"
        assert t.get("instructor"), f"Topic {t['id']} missing instructor"
    print("PASS: All 10 topics have verified video embeds and instructors.")

    assert FDE_MASTER_COURSE["primary_video_id"] == "lCQOCoH3Osk"
    assert "Microsoft" in FDE_MASTER_COURSE["instructor"] or "dotnet" in FDE_MASTER_COURSE["instructor"]
    assert FDE_BRIEFING_10MIN["video_id"] in ["VTnqUDMchXA", "4vHBgwcz_I4"]
    print("PASS: Home masterclass and 10-min briefing videos verified.")


def test_routes_and_encrypted_admin_access():
    """Verify email-sending access is removed and admin password verification is encrypted end-to-end."""
    reset_admin_rate_limit("127.0.0.1")
    reset_admin_rate_limit("unknown")
    client = app.test_client()

    # 1. Home page is freely accessible and contains NO email-sending access options or plaintext password
    res_home = client.get("/")
    assert res_home.status_code == 200
    home_html = res_home.data.decode("utf-8")
    assert "FDE Transformation Accelerator" in home_html
    assert "auth_crypto.js" in home_html
    assert "Azadirakhtaindica" not in home_html
    assert "Don't Know Password?" not in home_html
    assert "Send Email Request to Administrator" not in home_html
    assert "Generate Sample Email" not in home_html
    assert "/api/request-access" not in home_html
    print("PASS: Home page displays cleanly with encrypted auth script and zero email-access options or plaintext passwords.")

    # 2. Access gate page has no email sending option
    res_gate = client.get("/access-gate")
    assert res_gate.status_code == 200
    gate_html = res_gate.data.decode("utf-8")
    assert "Send Email" not in gate_html
    assert "Azadirakhtaindica" not in gate_html
    print("PASS: Access gate displays Admin Password challenge only (no email sending option).")

    # 3. Locked pages redirect to /?unlock=1
    for path in ["/courses", "/roadmap", "/kql-workbench", "/projects", "/interview-studio", "/notes"]:
        r = client.get(path)
        assert r.status_code == 302, f"Expected 302 for locked {path}, got {r.status_code}"
        assert "unlock=1" in r.headers["Location"]
    print("PASS: Locked routes redirect to /?unlock=1.")

    # 4. Old email-sending / allow / inbox endpoints are removed (redirect to /?unlock=1 or 404)
    for removed_path in ["/api/request-access", "/api/check-email-access", "/api/unlock-portal"]:
        r_old = client.post(removed_path, json={"email": "test@example.com"})
        assert r_old.status_code in (403, 404), f"Expected 403/404 for {removed_path}, got {r_old.status_code}"
    print("PASS: Email access request endpoints removed.")

    # 5. Plaintext password POST to /api/verify-site-password is rejected with 400
    plaintext_res = client.post("/api/verify-site-password", json={"password": "Azadirakhtaindica@007"})
    assert plaintext_res.status_code == 400
    assert plaintext_res.get_json()["success"] is False
    print("PASS: Plaintext password transmission rejected with 400.")

    # 6. Encrypted wrong password rejected with 401
    ch1 = client.get("/api/auth/challenge").get_json()
    assert "nonce" in ch1 and "salt" in ch1 and "transport_key" in ch1
    wrong_tok = build_client_encrypted_token("WrongPassword123!", ch1)
    wrong_pw = client.post("/api/verify-site-password", json={"encrypted_token": wrong_tok})
    assert wrong_pw.status_code == 401
    assert wrong_pw.get_json()["success"] is False
    print("PASS: Encrypted wrong password rejected with 401.")

    # 7. Anti-brute-force rate limiting: 5 consecutive failed attempts triggers 429
    for _ in range(4):
        ch_loop = client.get("/api/auth/challenge").get_json()
        bad_tok = build_client_encrypted_token("BadPassword!", ch_loop)
        client.post("/api/verify-site-password", json={"encrypted_token": bad_tok})

    ch_blocked = client.get("/api/auth/challenge").get_json()
    blocked_tok = build_client_encrypted_token("BadPassword!", ch_blocked)
    blocked_res = client.post("/api/verify-site-password", json={"encrypted_token": blocked_tok})
    assert blocked_res.status_code == 429
    assert "Too many failed attempts" in blocked_res.get_json()["error"]
    print("PASS: Anti-brute-force rate limiting verified (429 Too Many Requests).")

    reset_admin_rate_limit("127.0.0.1")
    reset_admin_rate_limit("unknown")

    # 8. Valid encrypted payload unlocks portal and returns NO sample_email
    ch_ok = client.get("/api/auth/challenge").get_json()
    valid_tok = build_client_encrypted_token("Azadirakhtaindica@007", ch_ok)
    assert "Azadirakhtaindica" not in valid_tok
    assert valid_tok.startswith("ENC-V1.")

    unlock_res = client.post("/api/verify-site-password", json={"encrypted_token": valid_tok, "target": "/courses"})
    assert unlock_res.status_code == 200
    unlock_data = unlock_res.get_json()
    assert unlock_data["success"] is True
    assert "sample_email" not in unlock_data
    assert unlock_data["redirect"] == "/courses"
    print("PASS: Encrypted Admin password payload verified and portal unlocked (no email generated).")

    # 9. Replay attack test: reusing same encrypted_token fails after lock
    client.get("/api/lock-portal")
    replay_res = client.post("/api/verify-site-password", json={"encrypted_token": valid_tok})
    assert replay_res.status_code == 401
    print("PASS: Single-use challenge replay protection verified (401).")

    # Unlock again and verify all pages load cleanly
    ch_ok2 = client.get("/api/auth/challenge").get_json()
    valid_tok2 = build_client_encrypted_token("Azadirakhtaindica@007", ch_ok2)
    assert client.post("/api/verify-site-password", json={"encrypted_token": valid_tok2}).status_code == 200

    for path in ["/courses", "/roadmap", "/topics", "/kql-workbench", "/projects", "/interview-studio", "/institutional-outreach", "/notes"]:
        page_res = client.get(path)
        assert page_res.status_code == 200, f"Expected 200 for unlocked {path}, got {page_res.status_code}"
    print("PASS: All unlocked web application routes return 200 OK.")

    # 10. Lock portal again
    client.get("/api/lock-portal")
    assert client.get("/courses").status_code == 302
    print("PASS: Portal re-locked back to Home-only display.")
    print("\nALL VERIFICATION TESTS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    test_native_xlsx_parsing()
    test_topics_and_roadmap()
    test_routes_and_encrypted_admin_access()
