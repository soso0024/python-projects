import datetime
import os.path
import sys
from dotenv import load_dotenv

import sqlite3

from dateutil import parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables from the .env file
load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/Users/soso/python-projects/time-manage/credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # determine which function to run
    if len(sys.argv) <= 1:
        print("Bad Request\nYou should provide a arguments like 'add' or 'commit'")
        exit()

    if sys.argv[1] == "add":
        if len(sys.argv) <= 3:
            print("You should provide duration and a title of plan")
            exit()
        duration = sys.argv[2]
        title = sys.argv[3]
        addEvent(creds, duration, title)

    if sys.argv[1] == "commit":
        if len(sys.argv) <= 1:
            print("You should provide day")
            exit()
        day = sys.argv[2]
        kind = sys.argv[3]
        commitHours(creds, day, kind)

    if sys.argv[1] == "get":
        if len(sys.argv) <= 2:
            print("You should provide duration of date")
            exit()
        duration = sys.argv[2]
        getHours(duration)


def commitHours(creds, day, kind):
    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        today = datetime.date.today()
        month_ago = today - datetime.timedelta(days=int(day))

        timeStart = str(month_ago) + "T00:00:00Z"
        timeEnd = str(today) + "T23:59:59Z"  # 'Z' indicates UTC time
        events_result = (
            service.events()
            .list(
                calendarId=os.getenv("SPORT_ID"),
                timeMin=timeStart,
                timeMax=timeEnd,
                singleEvents=True,
                orderBy="startTime",
                timeZone="Europe/Paris",
            )
            .execute()
        )
        events = events_result.get("items", [])

        # print(events)

        if not events:
            print("No upcoming events found.")
            return

        total_duration = datetime.timedelta(
            seconds=0,
            minutes=0,
            hours=0,
        )

        print("SPORT HOURS:")
        event_data = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            end = event["end"].get("dateTime", event["end"].get("date"))

            start_formatted = parser.isoparse(
                start
            )  # changing the start time to datetime format
            end_formatted = parser.isoparse(
                end
            )  # changing the end time to datetime format
            duration = end_formatted - start_formatted

            total_duration += duration
            print(f"{start}, {event['summary']}, duration: {duration}")

            event_type = "GYM"
            kind = None
            if event["summary"].upper() == "GYM":
                event_type = "GYM"
            if (
                event["summary"].upper() == "BASKET"
                or event["summary"].upper() == "BASKETBALL"
            ):
                event_type = "BASKETBALL"
                kind = "Club"

            event_data.append(
                (
                    start_formatted.date(),
                    event_type,
                    duration.total_seconds() / 3600,
                    kind,
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
                date, event_type, formatted_total_duration, kind = sport_data

                cur.execute(
                    "SELECT * FROM Sport WHERE DATE = ? AND CATEGORY = ?",
                    (date, event_type),
                )
                existing_row = cur.fetchone()

                if existing_row is None:
                    cur.execute("INSERT INTO Sport VALUES(?, ?, ?, ?);", sport_data)
                    conn.commit()
                    print("Sport Information added to database successfully")
                else:
                    print("The information already exists in the database.")

        except sqlite3.Error as error:
            print(f"Error Message: {error}")

    except HttpError as error:
        print(f"An error occurred: {error}")


def addEvent(creds, duration, description):
    start = datetime.datetime.utcnow()
    end = datetime.datetime.utcnow() + datetime.timedelta(hours=int(duration))

    start_formatted = start.isoformat() + "Z"
    end_formatted = end.isoformat() + "Z"

    event = {
        "summary": description,
        "start": {
            "dateTime": start_formatted,
            "timeZone": "Europe/Paris",
        },
        "end": {
            "dateTime": end_formatted,
            "timeZone": "Europe/Paris",
        },
    }

    service = build("calendar", "v3", credentials=creds)
    event = (
        service.events()
        .insert(
            calendarId=os.getenv("SPORT_ID"),
            body=event,
        )
        .execute()
    )
    print("Sport event created: %s" % (event.get("htmlLink")))


def getHours(duration):
    start = datetime.datetime.utcnow() - datetime.timedelta(days=int(duration))
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
            # print(row)

        print(
            f"Total Sport Times is {tol_times} hours in the last {int(duration) + 1} days.\nAverage Time is {tol_times / (int(duration) + 1)} hours."
        )

    except sqlite3.Error as error:
        print(error)


if __name__ == "__main__":
    main()
