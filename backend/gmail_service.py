"""
gmail_service.py — Google OAuth & Gmail API Service for Sahara.ai
Handles:
1. Google OAuth Flow (Authorization URL & Token Exchange)
2. Direct Email Dispatch via user's @gmail.com account using Gmail API
3. Inbox Auto-Syncing (scanning incoming emails for replies from institutions)
"""
import os
import json
import base64
import uuid
from datetime import datetime, timezone
import mimetypes
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict, Any

import httpx
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from database import User, Case, Task, Draft, TaskStatus

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


# ── Step 1: OAuth URLs & Token Exchange ────────────────────────────────────────

from urllib.parse import urlencode

def get_google_auth_url() -> str:
    """Returns Google OAuth authorization URL requesting Gmail scopes."""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
    }
    query = urlencode(params)
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query}"


def exchange_code_for_user(code: str, db: Session) -> Dict[str, Any]:
    """Exchanges authorization code for tokens and creates/updates User in DB."""
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    resp = httpx.post(token_url, data=data)
    if resp.status_code != 200:
        raise RuntimeError(f"Google OAuth token exchange failed: {resp.text}")

    tokens = resp.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    # Fetch User Info
    userinfo_resp = httpx.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    if userinfo_resp.status_code != 200:
        raise RuntimeError(f"Failed to fetch Google user profile: {userinfo_resp.text}")

    userinfo = userinfo_resp.json()
    google_id = userinfo.get("id")
    email = userinfo.get("email", "").lower()
    name = userinfo.get("name", email.split("@")[0])
    picture = userinfo.get("picture")

    # Find or create User
    user = db.query(User).filter((User.id == google_id) | (User.email == email)).first()
    if not user:
        user = User(
            id=google_id or str(uuid.uuid4()),
            email=email,
            name=name,
            picture=picture,
            password_hash="",
            google_refresh_token=refresh_token,
        )
        db.add(user)
    else:
        user.name = name
        user.picture = picture
        if refresh_token:
            user.google_refresh_token = refresh_token

    db.commit()
    db.refresh(user)

    return {
        "user": user,
        "access_token": access_token,
    }


def _get_user_credentials(user: User) -> Credentials:
    """Builds Google Credentials object for a user using their stored refresh token."""
    return Credentials(
        token=None,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES,
    )


# ── Step 2: Gmail Send Message ────────────────────────────────────────────────

def send_via_gmail_api(
    user: User,
    recipient_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Sends email directly from user's @gmail.com account using Gmail API."""
    if not user.google_refresh_token:
        raise RuntimeError("User has not authorized Gmail access. Please sign in with Google.")

    creds = _get_user_credentials(user)
    service = build("gmail", "v1", credentials=creds)

    msg = MIMEMultipart()
    msg["To"] = recipient_email
    msg["From"] = user.email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if attachments:
        for filepath in attachments:
            if filepath and os.path.exists(filepath) and os.path.isfile(filepath):
                filename = os.path.basename(filepath)
                ctype, encoding = mimetypes.guess_type(filepath)
                if ctype is None or encoding is not None:
                    ctype = "application/octet-stream"
                maintype, subtype = ctype.split("/", 1)

                with open(filepath, "rb") as f:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment", filename=filename)
                    msg.attach(part)

    raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    send_response = service.users().messages().send(userId="me", body={"raw": raw_message}).execute()

    return {
        "status": "sent",
        "message_id": send_response.get("id"),
        "thread_id": send_response.get("threadId"),
        "sent_from": user.email,
        "recipient": recipient_email,
    }


# ── Step 3: Gmail Inbox Auto-Syncing ──────────────────────────────────────────

def sync_inbox_for_replies(user: User, db: Session) -> Dict[str, Any]:
    """
    Scans user's Gmail inbox for incoming replies from institutions.
    Updates matching task status from SENT → COMPLETED when a reply is detected.
    """
    if not user.google_refresh_token:
        return {"status": "unauthorized", "updated_tasks": 0}

    creds = _get_user_credentials(user)
    service = build("gmail", "v1", credentials=creds)

    # Get all SENT tasks belonging to this user's cases
    user_cases = db.query(Case).filter((Case.user_id == user.id) | (Case.user_id.is_(None))).all()
    case_ids = [c.id for c in user_cases]

    sent_tasks = db.query(Task).filter(
        Task.case_id.in_(case_ids),
        Task.status == TaskStatus.SENT
    ).all()

    if not sent_tasks:
        return {"status": "success", "updated_tasks": 0, "message": "No pending sent tasks to check."}

    updated_count = 0
    synced_details = []

    for task in sent_tasks:
        # Search inbox for messages containing institution name or task type
        query = f'"{task.institution_name}" OR "{task.task_type}"'
        results = service.users().messages().list(userId="me", q=query, maxResults=5).execute()
        messages = results.get("messages", [])

        if messages:
            # Found a matching response thread!
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            updated_count += 1
            synced_details.append({
                "task_id": task.id,
                "institution": task.institution_name,
                "task_type": task.task_type,
            })

    db.commit()

    return {
        "status": "success",
        "updated_tasks": updated_count,
        "details": synced_details,
        "message": f"Inbox sync completed. Updated {updated_count} task(s) to Completed.",
    }
