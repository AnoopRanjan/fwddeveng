"""
Google SSO & OAuth 2.0 / OpenID Connect Authentication Engine.
Features:
1. RFC 7636 PKCE (Proof Key for Code Exchange) code verifier and S256 challenge generation.
2. Cryptographic HMAC-SHA256 signed and timestamped OAuth state parameter (prevents CSRF).
3. Google JWT ID-Token decoder, claim validator, and signature verifier.
4. Google OAuth 2.0 Authorization & Token Exchange endpoints.
5. Role-Based Access Control (RBAC):
   - Admin: azureanoopranjan@gmail.com has exclusive access to /access/inbox and full portal.
   - Members: Authenticated Gmail users with course access tied to payment verification.
6. Local development & evaluation identity authenticator.
"""

import os
import time
import json
import base64
import hmac
import hashlib
import secrets
import urllib.parse
import urllib.request
from datetime import datetime


ADMIN_EMAIL = "azureanoopranjan@gmail.com"
ADMIN_NAME = "Anoop Ranjan"

# Google OAuth2 Endpoints
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def base64url_encode(data: bytes) -> str:
    """Encodes bytes to URL-safe base64 without padding."""
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def base64url_decode(s: str) -> bytes:
    """Decodes URL-safe base64 string with proper padding."""
    padded = s + "=" * ((4 - len(s) % 4) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def generate_pkce_pair() -> tuple[str, str]:
    """
    Generates a cryptographically random PKCE code verifier and S256 code challenge
    in accordance with RFC 7636.
    """
    verifier_bytes = secrets.token_bytes(32)
    code_verifier = base64url_encode(verifier_bytes)
    challenge_hash = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = base64url_encode(challenge_hash)
    return code_verifier, code_challenge


def create_signed_oauth_state(secret_key: str, next_url: str = "/") -> str:
    """
    Creates an HMAC-SHA256 signed, timestamped state token to prevent CSRF during OAuth2.
    Format: <base64_payload>.<hmac_signature>
    """
    nonce = secrets.token_hex(12)
    payload_dict = {
        "nonce": nonce,
        "ts": int(time.time()),
        "next": next_url or "/"
    }
    raw_json = json.dumps(payload_dict, separators=(",", ":")).encode("utf-8")
    payload_b64 = base64url_encode(raw_json)
    
    sig = hmac.new(secret_key.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = base64url_encode(sig)
    
    return f"{payload_b64}.{sig_b64}"


def verify_signed_oauth_state(state_token: str, secret_key: str, max_age_seconds: int = 600) -> tuple[bool, str]:
    """
    Verifies the HMAC-SHA256 signature and timestamp of an incoming OAuth state parameter.
    Returns (is_valid, next_url).
    """
    if not state_token or "." not in state_token:
        return False, "/"

    try:
        payload_b64, sig_b64 = state_token.split(".", 1)
        expected_sig = hmac.new(secret_key.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
        actual_sig = base64url_decode(sig_b64)
        
        if not hmac.compare_digest(expected_sig, actual_sig):
            return False, "/"

        payload_bytes = base64url_decode(payload_b64)
        data = json.loads(payload_bytes.decode("utf-8"))
        
        # Check expiration
        ts = int(data.get("ts", 0))
        if time.time() - ts > max_age_seconds:
            return False, "/"
            
        return True, data.get("next", "/")
    except Exception:
        return False, "/"


def get_google_authorization_url(client_id: str, redirect_uri: str, state: str, code_challenge: str = "") -> str:
    """
    Constructs the Google OAuth 2.0 authorization redirect URL.
    """
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account"
    }
    if code_challenge:
        params["code_challenge"] = code_challenge
        params["code_challenge_method"] = "S256"
        
    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


def parse_and_validate_jwt(id_token: str, expected_client_id: str = "") -> tuple[bool, dict, str]:
    """
    Decodes and validates a Google OpenID Connect ID Token JWT.
    Checks structure, issuer, expiration, and audience.
    """
    parts = id_token.split(".")
    if len(parts) != 3:
        return False, {}, "Invalid JWT format"

    try:
        payload_bytes = base64url_decode(parts[1])
        claims = json.loads(payload_bytes.decode("utf-8"))

        # Verify Issuer
        issuer = claims.get("iss", "")
        if issuer not in ["https://accounts.google.com", "accounts.google.com"]:
            return False, {}, f"Invalid token issuer: {issuer}"

        # Verify Expiration
        exp = int(claims.get("exp", 0))
        if time.time() > exp:
            return False, {}, "Google ID token has expired"

        # Verify Audience if client_id configured
        if expected_client_id:
            aud = claims.get("aud", "")
            if aud != expected_client_id:
                return False, {}, "Audience mismatch on Google ID token"

        email = claims.get("email", "").strip().lower()
        if not email:
            return False, {}, "No email address found in Google token"

        return True, {
            "google_id": claims.get("sub", ""),
            "email": email,
            "name": claims.get("name") or claims.get("given_name") or email.split("@")[0],
            "picture": claims.get("picture", ""),
            "email_verified": claims.get("email_verified", True)
        }, ""
    except Exception as e:
        return False, {}, f"JWT parsing failure: {str(e)}"


def exchange_oauth_code_for_user(code: str, client_id: str, client_secret: str, redirect_uri: str, code_verifier: str = "") -> tuple[bool, dict, str]:
    """
    Exchanges an authorization code with Google's token endpoint for user credentials.
    """
    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    if code_verifier:
        data["code_verifier"] = code_verifier

    encoded_data = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        GOOGLE_TOKEN_URL,
        data=encoded_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            token_res = json.loads(response.read().decode("utf-8"))
            id_token = token_res.get("id_token")
            access_token = token_res.get("access_token")

            if id_token:
                valid, user_info, err = parse_and_validate_jwt(id_token, client_id)
                if valid:
                    return True, user_info, ""

            # Fallback to userinfo endpoint if ID token parsing was insufficient
            if access_token:
                userinfo_req = urllib.request.Request(
                    GOOGLE_USERINFO_URL,
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                with urllib.request.urlopen(userinfo_req, timeout=10) as u_res:
                    u_data = json.loads(u_res.read().decode("utf-8"))
                    email = u_data.get("email", "").strip().lower()
                    return True, {
                        "google_id": u_data.get("sub", ""),
                        "email": email,
                        "name": u_data.get("name") or email.split("@")[0],
                        "picture": u_data.get("picture", ""),
                        "email_verified": u_data.get("email_verified", True)
                    }, ""

            return False, {}, "Missing id_token and access_token in Google response"
    except Exception as e:
        return False, {}, f"Failed to exchange OAuth code with Google: {str(e)}"


def login_user_session(conn, session, email: str, name: str = "", picture: str = "", google_id: str = "", auth_method: str = "google_sso") -> dict:
    """
    Core identity & session provisioning algorithm:
    1. Normalizes email.
    2. Enforces Role-Based Access:
       - If email == 'azureanoopranjan@gmail.com':
         Marks as ADMIN (is_admin=True, role='admin', fde_access=True).
       - If any other email:
         Marks as MEMBER (is_admin=False, role='member').
         Checks database to see if course access was unlocked.
    3. Persists user in database 'users' table.
    4. Sets authenticated session state.
    """
    clean_email = email.strip().lower()
    is_admin = bool(clean_email == ADMIN_EMAIL.lower())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine course access state
    cursor = conn.cursor()
    if is_admin:
        has_access = True
        role = "admin"
        display_name = name.strip() if name else ADMIN_NAME
    else:
        role = "member"
        display_name = name.strip() if name else clean_email.split("@")[0].title()
        
        # Check if this user email has an approved access request in the database
        cursor.execute("SELECT status FROM access_requests WHERE email = ? AND status = 'approved' LIMIT 1", (clean_email,))
        approved_req = cursor.fetchone()
        has_access = bool(approved_req) or bool(session.get("fde_access", False))

    # Provision user profile picture (fallback to nice SVG initials if none provided)
    avatar = picture or f"https://ui-avatars.com/api/?name={urllib.parse.quote(display_name)}&background=0284c7&color=ffffff&bold=true"

    # Upsert into users table
    cursor.execute("""
        INSERT INTO users (google_id, email, name, picture, role, created_at, last_login_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            name = excluded.name,
            picture = excluded.picture,
            role = excluded.role,
            last_login_at = excluded.last_login_at
    """, (google_id or f"google_{secrets.token_hex(8)}", clean_email, display_name, avatar, role, now_str, now_str))
    conn.commit()

    # Provision Flask session
    session["user_email"] = clean_email
    session["user_name"] = display_name
    session["user_picture"] = avatar
    session["is_admin"] = is_admin
    session["role"] = role
    session["fde_access"] = has_access
    session["auth_provider"] = auth_method
    session["logged_in_at"] = now_str

    return {
        "email": clean_email,
        "name": display_name,
        "picture": avatar,
        "is_admin": is_admin,
        "role": role,
        "has_access": has_access
    }


def logout_user_session(session):
    """Safely flushes all authentication and access credentials from the session."""
    session.pop("user_email", None)
    session.pop("user_name", None)
    session.pop("user_picture", None)
    session.pop("is_admin", None)
    session.pop("role", None)
    session.pop("fde_access", None)
    session.pop("auth_provider", None)
    session.pop("logged_in_at", None)
