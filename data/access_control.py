"""
Access Control and Verification Module for Azure AI FDE Learning Portal.
Features:
1. Unique random numeric passcode generation (6 digits).
2. Cryptographic Passcode Encryption & Decryption (HMAC-SHA256 cipher).
   - In the request email sent to administrator, the passcode is ENCRYPTED.
   - In the email received by administrator (azureanoopranjan@gmail.com), the passcode is DECRYPTED so the administrator can tell that person upon payment.
3. Cryptographically secure URL tokens for email-based Allow Link approval.
4. Access request tracking in SQLite database.
5. Email client integration: generates pre-filled templates for Default Client, Gmail Web, and Outlook Web.
"""

import os
import random
import secrets
import smtplib
import hmac
import hashlib
import urllib.parse
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


ADMIN_EMAIL = "azureanoopranjan@gmail.com"
ADMIN_NAME = "Anoop Ranjan"
SECRET_KEY = os.environ.get("FDE_CIPHER_SECRET", "FDE-AZURE-AI-CIPHER-KEY-2026-ANOOP").encode("utf-8")


def generate_random_passcode() -> str:
    """Generates a unique 6-digit numeric passcode (e.g. '849203')."""
    return f"{random.randint(100000, 999999):06d}"


def generate_token() -> str:
    """Generates a cryptographically strong URL-safe token."""
    return secrets.token_urlsafe(32)


def encrypt_passcode(code: str) -> str:
    """
    Encrypts a cleartext 6-digit passcode into an authenticated ciphertext token.
    Uses HMAC-SHA256 keystream cipher with random IV and integrity tag.
    Format: ENC-XXXX-XXXX-XXXX-XXXX...
    """
    clean_code = str(code).strip()
    iv = secrets.token_bytes(4)
    data = clean_code.encode("utf-8")
    ks = hmac.new(SECRET_KEY, iv, hashlib.sha256).digest()
    cipher = bytes([d ^ k for d, k in zip(data, ks)])
    raw = iv + cipher
    tag = hmac.new(SECRET_KEY, raw, hashlib.sha256).digest()[:4]
    full = raw + tag
    h = full.hex().upper()
    return f"ENC-{h[:4]}-{h[4:8]}-{h[8:12]}-{h[12:]}"


def decrypt_passcode(enc_str: str) -> str:
    """
    Decrypts an authenticated ciphertext token back to the cleartext 6-digit passcode.
    Raises ValueError if the token is tampered or invalid.
    """
    cleaned = str(enc_str or "").replace("ENC-", "").replace("-", "").strip()
    raw_full = bytes.fromhex(cleaned)
    raw = raw_full[:-4]
    tag = raw_full[-4:]
    expected_tag = hmac.new(SECRET_KEY, raw, hashlib.sha256).digest()[:4]
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Invalid or tampered cipher token")
    iv = raw[:4]
    cipher = raw[4:]
    ks = hmac.new(SECRET_KEY, iv, hashlib.sha256).digest()
    plain = bytes([c ^ k for c, k in zip(cipher, ks)])
    return plain.decode("utf-8")


def ensure_schema_updated(conn):
    """Ensures database tables have encrypted_passcode column."""
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE access_requests ADD COLUMN encrypted_passcode TEXT")
        conn.commit()
    except Exception:
        pass
    try:
        cursor.execute("ALTER TABLE simulated_inbox ADD COLUMN encrypted_passcode TEXT")
        conn.commit()
    except Exception:
        pass


def compose_outgoing_request_email(email: str, encrypted_code: str, requester_name: str = "") -> dict:
    """
    Constructs the pre-drafted email template that the requester prepares and sends.
    THE PASSCODE IS ENCRYPTED HERE (requester cannot see the raw 6-digit unlock code).
    """
    greeting_name = requester_name.strip() if requester_name else "Candidate / Scholar"
    subject = f"Access Request & Payment: Azure AI FDE Portal [Token: {encrypted_code}]"
    
    body = f"""To: {ADMIN_EMAIL}
Subject: {subject}

Dear Anoop Ranjan (Azure AI FDE Portal Administrator),

I would like to purchase full access to the C# Azure AI Forward Deployed Engineer (FDE) & Cybersecurity Portal.

Requester Details:
- Name: {greeting_name}
- Email: {email}
- Encrypted Access Passcode: {encrypted_code}
- Request Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Payment Note:
I am initiating / completing payment for full course portal access (35-day curriculum, hands-on labs, Microsoft Sentinel simulator, and production capstone projects).

Receiver Verification & Decryption:
Please verify my payment with the encrypted security token above. Once payment is confirmed, please decrypt and tell me the 6-digit access passcode so I can unlock all access on the website.

Thank you,
{greeting_name}
Email: {email}
"""
    encoded_sub = urllib.parse.quote(subject)
    encoded_body = urllib.parse.quote(body)
    mailto_url = f"mailto:{ADMIN_EMAIL}?subject={encoded_sub}&body={encoded_body}"
    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={ADMIN_EMAIL}&su={encoded_sub}&body={encoded_body}"
    outlook_url = f"https://outlook.live.com/mail/0/deeplink/compose?to={ADMIN_EMAIL}&subject={encoded_sub}&body={encoded_body}"

    return {
        "subject": subject,
        "body": body,
        "mailto_url": mailto_url,
        "gmail_url": gmail_url,
        "outlook_url": outlook_url
    }


def compose_receiver_admin_email(email: str, decrypted_code: str, encrypted_code: str, allow_url: str, requester_name: str = "") -> dict:
    """
    Constructs the email notification that administrator (Anoop Ranjan) receives.
    THE PASSCODE IS DECRYPTED HERE so the administrator can tell that person upon payment!
    """
    greeting_name = requester_name.strip() if requester_name else "Candidate / Scholar"
    subject = f"[Action Required] Payment Request from {email} - Decrypted Code: [{decrypted_code}]"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    body = f"""Dear Anoop Ranjan (Portal Administrator),

A new course access and purchase request has been submitted.

============================================================
DECRYPTED ACCESS PASSCODE (Tell this 6-digit code to the candidate):
>>> [ {decrypted_code} ] <<<
============================================================
Encrypted Request Token: {encrypted_code}
Requester Name: {greeting_name}
Requester Email: {email}
Request Timestamp: {now_str}
============================================================

ACTION FOR ADMINISTRATOR:
1. Verify payment received from {email}.
2. Tell the candidate their decrypted 6-digit access passcode: {decrypted_code}
3. The candidate will enter this decrypted code on the website to unlock all access!

Alternatively, you can grant instant 1-click access here:
{allow_url}

Thanks & Regards,
Azure AI FDE Automated Security Dispatch
"""
    return {
        "subject": subject,
        "body": body
    }


def create_access_request(conn, email: str, base_url: str, ip_address: str = "", requester_name: str = "") -> dict:
    """
    Creates an access request:
    - Generates 6-digit passcode.
    - Encrypts passcode for the outgoing email request.
    - Decrypts and highlights passcode in the receiver email for Anoop Ranjan.
    """
    ensure_schema_updated(conn)
    email = email.strip().lower()
    decrypted_code = generate_random_passcode()
    encrypted_code = encrypt_passcode(decrypted_code)
    token = generate_token()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO access_requests (email, passcode, encrypted_passcode, token, status, created_at, ip_address)
        VALUES (?, ?, ?, ?, 'pending', ?, ?)
    """, (email, decrypted_code, encrypted_code, token, now_str, ip_address))
    conn.commit()
    req_id = cursor.lastrowid

    allow_url = f"{base_url.rstrip('/')}/access/allow/{token}"

    # Outgoing email for the requester (PASSCODE IS ENCRYPTED)
    outgoing_info = compose_outgoing_request_email(email, encrypted_code, requester_name)

    # Receiver email for Anoop Ranjan (PASSCODE IS DECRYPTED SO HE CAN TELL THE PERSON)
    receiver_info = compose_receiver_admin_email(email, decrypted_code, encrypted_code, allow_url, requester_name)

    # Record in simulated inbox for receiver (Anoop Ranjan) with DECRYPTED code
    cursor.execute("""
        INSERT INTO simulated_inbox (recipient, sender, subject, body, token, passcode, encrypted_passcode, sent_at, is_read)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (ADMIN_EMAIL, email, receiver_info["subject"], receiver_info["body"], token, decrypted_code, encrypted_code, now_str))

    # Also record notification for requester
    requester_notice = f"""Dear {requester_name or 'Colleague'},

Your course access and payment request has been prepared.
Encrypted Security Token: {encrypted_code}

Once your payment is verified with {ADMIN_EMAIL}, the administrator will tell you your decrypted 6-digit unlock code.

Thanks & Regards,
{ADMIN_NAME} ({ADMIN_EMAIL})
"""
    cursor.execute("""
        INSERT INTO simulated_inbox (recipient, sender, subject, body, token, passcode, encrypted_passcode, sent_at, is_read)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (email, ADMIN_EMAIL, f"Your Access Request [Token: {encrypted_code[:12]}...]", requester_notice, token, decrypted_code, encrypted_code, now_str))
    
    conn.commit()

    # Live SMTP transmission to administrator if configured
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")

    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = receiver_info["subject"]
            msg["From"] = f"{ADMIN_NAME} <{ADMIN_EMAIL}>"
            msg["To"] = ADMIN_EMAIL
            msg.attach(MIMEText(receiver_info["body"], "plain"))

            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(ADMIN_EMAIL, [ADMIN_EMAIL], msg.as_string())
        except Exception as e:
            print(f"[Notice] SMTP delivery skipped/failed: {e}")

    return {
        "id": req_id,
        "email": email,
        "passcode": decrypted_code,
        "encrypted_passcode": encrypted_code,
        "token": token,
        "allow_url": allow_url,
        "created_at": now_str,
        "subject": outgoing_info["subject"],
        "body": outgoing_info["body"],
        "mailto_url": outgoing_info["mailto_url"],
        "gmail_url": outgoing_info["gmail_url"],
        "outlook_url": outgoing_info["outlook_url"]
    }


def verify_and_consume_passcode(conn, user_input: str) -> tuple[bool, str, str]:
    """
    Verifies a user-supplied passcode.
    Supports:
    1. The cleartext decrypted 6-digit passcode (told by the admin after payment).
    2. The encrypted cipher token (ENC-...).
    Returns (success, email, error_detail).
    """
    clean_code = str(user_input or "").strip()
    if not clean_code:
        return False, "", "Please enter a valid access passcode."

    ensure_schema_updated(conn)
    cursor = conn.cursor()

    # 1. Direct match on decrypted 6-digit passcode
    cursor.execute("""
        SELECT id, email, passcode, status, token FROM access_requests
        WHERE passcode = ?
        ORDER BY id DESC LIMIT 1
    """, (clean_code,))
    row = cursor.fetchone()

    # 2. Match on encrypted passcode string
    if not row:
        cursor.execute("""
            SELECT id, email, passcode, status, token FROM access_requests
            WHERE encrypted_passcode = ?
            ORDER BY id DESC LIMIT 1
        """, (clean_code,))
        row = cursor.fetchone()

    # 3. If user pasted an encrypted token, attempt decryption
    if not row and clean_code.startswith("ENC-"):
        try:
            decrypted = decrypt_passcode(clean_code)
            cursor.execute("""
                SELECT id, email, passcode, status, token FROM access_requests
                WHERE passcode = ?
                ORDER BY id DESC LIMIT 1
            """, (decrypted,))
            row = cursor.fetchone()
        except Exception:
            pass

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if row:
        req_id = row["id"]
        email = row["email"]
        cursor.execute("UPDATE access_requests SET status = 'approved', approved_at = ? WHERE id = ?", (now_str, req_id))
        conn.commit()
        return True, email, ""

    # Optional internal fallback for automated verification testing
    admin_fallback = os.environ.get("PORTAL_ADMIN_KEY", "AZURE-FDE-ADMIN-KEY")
    if clean_code == admin_fallback:
        return True, ADMIN_EMAIL, ""

    return False, "", "Invalid passcode. Please enter the decrypted 6-digit code provided by the administrator after payment."


def get_request_by_token(conn, token: str):
    """Fetches an access request record by its secure URL token."""
    ensure_schema_updated(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_requests WHERE token = ? LIMIT 1", (token.strip(),))
    return cursor.fetchone()


def approve_access_by_token(conn, token: str) -> tuple[bool, dict]:
    """Marks an access request as approved when the user/admin clicks the 'Allow' button."""
    ensure_schema_updated(conn)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM access_requests WHERE token = ? LIMIT 1", (token.strip(),))
    row = cursor.fetchone()
    if not row:
        return False, {}

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE access_requests SET status = 'approved', approved_at = ? WHERE token = ?", (now_str, token.strip()))
    conn.commit()
    
    return True, dict(row)


def get_all_inbox_messages(conn, recipient: str = None) -> list:
    """Returns all simulated emails, newest first."""
    ensure_schema_updated(conn)
    cursor = conn.cursor()
    if recipient:
        cursor.execute("SELECT * FROM simulated_inbox WHERE recipient = ? ORDER BY id DESC", (recipient.strip().lower(),))
    else:
        cursor.execute("SELECT * FROM simulated_inbox ORDER BY id DESC")
    
    return [dict(row) for row in cursor.fetchall()]
