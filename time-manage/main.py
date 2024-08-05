import datetime
import os.path
import argparse
from dotenv import load_dotenv
import sqlite3
from dateutil import parser
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# import sys
# import pytz

# Load environment variables from the .env file
load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/Users/soso/python-projects/time-manage/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def add_event(args):
    creds = get_credentials()
    start = datetime.datetime.utcnow() - datetime.timedelta(hours=int(args.hours_ago))
    end = start + datetime.timedelta(hours=int(args.duration))

    start_formatted = start.isoformat() + "Z"
    end_formatted = end.isoformat() + "Z"

    event = {
        "summary": args.title,
        "start": {
            "dateTime": start_formatted,
            "timeZone": "Asia/Tokyo",
        },
        "end": {
            "dateTime": end_formatted,
            "timeZone": "Asia/Tokyo",
        },
    }

    service = build("calendar", "v3", credentials=creds)

    id_type = "GENERAL_ID" if args.id_type.upper() == "GENERAL" else "SPORT_ID"

    event = service.events().insert(calendarId=os.getenv(id_type), body=event).execute()
    print("Event created: %s" % (event.get("htmlLink")))


def commit_hours(args):
    creds = get_credentials()
    try:
        service = build("calendar", "v3", credentials=creds)

        today = datetime.date.today()
        month_ago = today - datetime.timedelta(days=int(args.day))

        timeStart = str(month_ago) + "T00:00:00Z"
        timeEnd = str(today) + "T23:59:59Z"
        events_result = (
            service.events()
            .list(
                calendarId=os.getenv("SPORT_ID"),
                timeMin=timeStart,
                timeMax=timeEnd,
                singleEvents=True,
                orderBy="startTime",
                timeZone="Asia/Tokyo",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        total_duration = datetime.timedelta(seconds=0, minutes=0, hours=0)

        print("SPORT HOURS:")
        event_data = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            start_formatted = parser.isoparse(start)
            end_formatted = parser.isoparse(end)
            duration = end_formatted - start_formatted

            total_duration += duration
            print(f"{start}, {event['summary']}, duration: {duration}")

            event_type = "Some Activity"
            if event["summary"].upper() == "GYM":
                event_type = "GYM"
            if event["summary"].upper() in ["BASKET", "BASKETBALL"]:
                event_type = "BASKETBALL"

            event_data.append(
                (
                    start_formatted.date(),
                    event_type,
                    duration.total_seconds() / 3600,
                )
            )

        print(f"Total sport time: {total_duration}")

        try:
            conn = sqlite3.connect(
                "/Users/soso/python-projects/time-manage/sport.sqlite3"
            )
            cur = conn.cursor()
            print("Opened database successfully")

            for sport_data in event_data:
                date, event_type, formatted_total_duration = sport_data

                cur.execute(
                    "SELECT * FROM Sport WHERE DATE = ? AND CATEGORY = ?",
                    (date, event_type),
                )
                existing_row = cur.fetchone()

                if existing_row is None:
                    cur.execute("INSERT INTO Sport VALUES(?, ?, ?);", sport_data)
                    conn.commit()
                    print("Sport Information added to database successfully")
                else:
                    print("The information already exists in the database.")

        except sqlite3.Error as error:
            print(f"Error Message: {error}")

    except HttpError as error:
        print(f"An error occurred: {error}")


def get_hours(args):
    start = datetime.datetime.utcnow() - datetime.timedelta(days=int(args.duration))
    end = datetime.datetime.utcnow()

    tol_times = 0
    try:
        conn = sqlite3.connect("/Users/soso/python-projects/time-manage/sport.sqlite3")
        cur = conn.cursor()
        cur.execute(
            "SELECT HOURS FROM sport WHERE DATE BETWEEN ? AND ?",
            (f"{start:%Y-%m-%d}", f"{end:%Y-%m-%d}"),
        )
        rows = cur.fetchall()
        for row in rows:
            tol_times += row[0]

        print(
            f"Total Sport Times is {tol_times} hours in the last {int(args.duration)} days.\n"
            f"Average Time is {tol_times / (int(args.duration))} hours."
        )

    except sqlite3.Error as error:
        print(error)


def get_upcoming_events(args):
    creds = get_credentials()
    try:
        service = build("calendar", "v3", credentials=creds)
        # jp_tz = pytz.timezone("Asia/Tokyo")
        # now = datetime.datetime.now(jp_tz).isoformat()
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        print(f"Getting the upcoming {args.max_results} events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=args.max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the upcoming events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(f"{start} - {event['summary']}")

    except HttpError as error:
        print(f"An error occurred: {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Google Calendar API Integration for Sports Tracking"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add event parser
    add_parser = subparsers.add_parser("add", help="Add a new event")
    add_parser.add_argument(
        "id_type",
        choices=["general", "sport"],
        help="Type of calendar (general or sport)",
    )
    add_parser.add_argument(
        "duration",
        type=int,
        help="Duration of the event in hours",
    )
    add_parser.add_argument(
        "title",
        help="Title of the event",
    )
    add_parser.add_argument(
        "hours_ago",
        type=int,
        help="Hours ago the event started (positive for past, negative for future)",
    )
    add_parser.set_defaults(func=add_event)

    # Commit hours parser
    commit_parser = subparsers.add_parser("commit", help="Commit hours to database")
    commit_parser.add_argument(
        "day",
        type=int,
        help="Days ago (0 for today)",
    )
    commit_parser.set_defaults(func=commit_hours)

    # Get hours parser
    get_parser = subparsers.add_parser("get", help="Get total hours for a duration")
    get_parser.add_argument(
        "--duration",
        type=int,
        default=10,
        help="Duration in days",
    )
    get_parser.set_defaults(func=get_hours)

    # Get upcoming events parser
    upcoming_parser = subparsers.add_parser("upcoming", help="Get upcoming events")
    upcoming_parser.add_argument(
        "--max_results",
        type=int,
        default=10,
        help="Maximum number of events to retrieve (default: 10)",
    )
    upcoming_parser.set_defaults(func=get_upcoming_events)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()
