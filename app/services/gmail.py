import os
import pickle
import base64
import urllib.parse
from pathlib import Path
from email.mime.text import MIMEText

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = Path("credentials.json")
TOKEN_FILE = Path("gmail_token.pickle")


def get_client_config():
    import json
    with open(CREDENTIALS_FILE) as f:
        return json.load(f)["installed"]


def auth_url():
    c = get_client_config()
    params = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": c["client_id"],
        "redirect_uri": "http://localhost",
        "scope": SCOPES[0],
        "access_type": "offline",
        "prompt": "consent",
    })
    url = f"{c['auth_uri']}?{params}"
    print("=" * 60)
    print(" Ve al siguiente enlace en tu navegador:")
    print(f" {url}")
    print("=" * 60)
    print("Inicia sesion, acepta los permisos y copia el codigo de la URL")
    print("(despues de ?code=...)")
    print("Luego ejecuta: python -c \"from app.services.gmail import save_token; save_token('CODIGO')\"")


def save_token(code):
    c = get_client_config()
    resp = requests.post(c["token_uri"], data={
        "code": code,
        "client_id": c["client_id"],
        "client_secret": c["client_secret"],
        "redirect_uri": "http://localhost",
        "grant_type": "authorization_code",
    })
    data = resp.json()
    if "error" in data:
        print(f"ERROR: {data.get('error')} - {data.get('error_description', '')}")
        return
    creds = Credentials(
        token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        token_uri=c["token_uri"],
        client_id=c["client_id"],
        client_secret=c["client_secret"],
        scopes=SCOPES,
    )
    with open(TOKEN_FILE, "wb") as f:
        pickle.dump(creds, f)
    print("Token de Gmail guardado correctamente.")


def get_service():
    creds = None
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, "wb") as f:
                pickle.dump(creds, f)
        else:
            print("No hay token valido. Genera uno primero.")
            auth_url()
            return None
    return build("gmail", "v1", credentials=creds)


class GmailService:
    def __init__(self):
        self.service = get_service()

    def is_ready(self):
        return self.service is not None

    def send_email(self, to: str, subject: str, body: str) -> dict | None:
        if not self.service:
            return None
        try:
            message = MIMEText(body, "plain", "utf-8")
            message["to"] = to
            message["subject"] = subject
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
            result = self.service.users().messages().send(
                userId="me", body={"raw": raw}
            ).execute()
            return result
        except HttpError as e:
            print(f"Gmail send error: {e}")
            return None

    def read_inbox(self, max_results: int = 5) -> list[dict]:
        if not self.service:
            return []
        try:
            results = self.service.users().messages().list(
                userId="me", maxResults=max_results, q="is:unread"
            ).execute()
            messages = results.get("messages", [])
            parsed = []
            for msg in messages:
                details = self.service.users().messages().get(
                    userId="me", id=msg["id"]
                ).execute()
                headers = {h["name"]: h["value"] for h in details["payload"]["headers"]}
                parsed.append({
                    "id": msg["id"],
                    "from": headers.get("From", ""),
                    "subject": headers.get("Subject", ""),
                    "date": headers.get("Date", ""),
                    "references": headers.get("References", headers.get("Message-ID", "")),
                    "snippet": details.get("snippet", ""),
                })
            return parsed
        except HttpError as e:
            print(f"Gmail read error: {e}")
            return []

    def mark_as_read(self, message_id: str) -> bool:
        if not self.service:
            return False
        try:
            self.service.users().messages().modify(
                userId="me",
                id=message_id,
                body={"removeLabelIds": ["UNREAD"]},
            ).execute()
            return True
        except HttpError:
            return False
