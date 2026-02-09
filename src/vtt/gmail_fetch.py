from typing import List, Dict

def list_messages(service, query: str, max_results: int = 10) -> List[str]:
    resp = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    return [m["id"] for m in resp.get("messages", [])]

def get_message_brief(service, msg_id: str) -> Dict:
    msg = service.users().messages().get(
        userId="me", id=msg_id, format="metadata",
        metadataHeaders=["From", "Subject", "Date"]
    ).execute()
    
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
