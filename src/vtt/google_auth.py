from asyncio import ensure_future
from typing import List
import os
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from oauthlib.oauth2.rfc6749.utils import scope_to_list
import json


from vtt import root_path

CRED = root_path / "cred" / "credentials.json"
TOKEN = root_path / "cred" / "token.json"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def get_google_service(
    api_name: str,
    api_version: str,
    scopes: List[str] = SCOPES,
    credentials_path=CRED,
    token_path=TOKEN,
):
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(
            f"找不到 {credentials_path}，請把從 Google Cloud 下載的 JSON 命名為 credentials.json"
        )

    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w", encoding="utf-8") as f:
            f.write(creds.to_json())

    return build(api_name, api_version, credentials=creds)


def list_messages(service, query: str, max_results: int = 10) -> List[str]:
    resp = (
        service.users()
        .messages()
        .list(userId="me", q=query, maxResults=max_results)
        .execute()
    )
    return [m["id"] for m in resp.get("messages", [])]


def get_message_brief(service, msg_id: str) -> Dict:
    msg = (
        service.users()
        .messages()
        .get(
            userId="me",
            id=msg_id,
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"],
        )
        .execute()
    )

    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    snippet = msg.get("snippet", "")

    return {
        "id": msg_id,
        "from": headers.get("From", ""),
        "subject": headers.get("Subject", ""),
        "date": headers.get("Date", ""),
        "snippet": snippet,
    }


def fetch_emails(service, query: str, max_results: int = 8) -> List[Dict]:
    ids = list_messages(service, query=query, max_results=max_results)
    return [get_message_brief(service, mid) for mid in ids]


def fetch_calendars(service, start: int = 0, end: int = 7) -> List[Dict]:

    # 設定時間
    tz = timezone(timedelta(hours=8))  # Taipei
    tomorrow = (datetime.now(tz) + timedelta(days=start)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    week_after = tomorrow + timedelta(days=end)

    events = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=tomorrow.astimezone(timezone.utc).isoformat(),
            timeMax=week_after.astimezone(timezone.utc).isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )

    infos = []
    for item in events:
        time_start = item.get("start", {}).get("date", {})
        time_end = item.get("end", {}).get("date", {})
        title = item.get("summary", "")

        info = {}
        info["time_start"] = time_start
        info["time_end"] = time_end
        info["title"] = title

        infos.append(info)

    return infos


if __name__ == "__main__":
    gmail = get_google_service("gmail", "v1")
    calendar = get_google_service("calendar", "v3")

    gmail_info = fetch_emails(gmail, "newer_than:1d", 10)
    calendar_info = fetch_calendars(calendar)

    print(json.dumps(gmail_info, ensure_ascii=False, indent=4))
    print(json.dumps(calendar_info, ensure_ascii=False, indent=4))
