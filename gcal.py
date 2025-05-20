import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# If modifying SCOPES, delete token.json
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None
    if os.path.exists("auth/token.json"):
        creds = Credentials.from_authorized_user_file("auth/token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "auth/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("auth/token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    return service


def list_upcoming_events(max_results=5):
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"
    events_result = (
        service.events()
        .list(calendarId="primary", timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime")
        .execute()
    )
    events = events_result.get("items", [])

    simplified = []
    for event in events:
        summary = event.get("summary", "(No title)")
        start = event["start"].get("dateTime", event["start"].get("date"))
        simplified.append({"summary": summary, "start": start})

    return simplified


def create_event(event):
    service = get_calendar_service()

    # Parse basic plain-English time to RFC3339 (you can improve this later)
    start_time = event['start']
    duration_minutes = event['duration']
    now = datetime.datetime.now()

    try:
        start = datetime.datetime.strptime(start_time, "%I%p")
        start = start.replace(year=now.year, month=now.month, day=now.day)
    except ValueError:
        start = now + datetime.timedelta(minutes=5)  # fallback

    end = start + datetime.timedelta(minutes=duration_minutes)

    body = {
        "summary": event['summary'],
        "start": {"dateTime": start.isoformat(), "timeZone": "America/Chicago"},
        "end": {"dateTime": end.isoformat(), "timeZone": "America/Chicago"},
    }

    created_event = service.events().insert(calendarId="primary", body=body).execute()
    print(f"📅 Created: {created_event.get('summary')} at {created_event.get('start').get('dateTime')}")
