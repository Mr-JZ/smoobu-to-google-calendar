from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
from typing import List
import pickle
import os
import json
import logging
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger("google_calendar")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app-google-calendar.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

load_dotenv()


@dataclass
class EventTime:
    dateTime: datetime
    timeZone: str = os.getenv("TIME_ZONE")

    def to_dict(self):
        # Localize the datetime to the specified time zone
        tzinfo = ZoneInfo(self.timeZone)
        localized_dt = self.dateTime.astimezone(tzinfo)
        # Format datetime to 'YYYY-MM-DDTHH:MM:SS±HH:MM'
        dateTime_str = localized_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
        # Insert a colon in the timezone offset to match ISO 8601 format
        dateTime_str = dateTime_str[:-2] + ":" + dateTime_str[-2:]
        return {"dateTime": dateTime_str, "timeZone": self.timeZone}


@dataclass
class EventAttendee:
    email: str

    def to_dict(self):
        return {"email": self.email}


@dataclass
class EventReminderOverride:
    method: str
    minutes: int

    def to_dict(self):
        return {"method": self.method, "minutes": self.minutes}


@dataclass
class EventReminder:
    useDefault: bool
    overrides: List[EventReminderOverride]

    def to_dict(self):
        return {
            "useDefault": self.useDefault,
            "overrides": [
                override.to_dict() for override in self.overrides
            ],  # Manually call to_json for each override
        }


@dataclass
class GoogleCalendarEvent:
    summary: str
    location: str
    description: str
    start: EventTime
    end: EventTime
    recurrence: List[str] = None
    attendees: List[EventAttendee] = None
    reminders: EventReminder = EventReminder(useDefault=True, overrides=[])

    def to_dict(self):
        attendees = []
        if self.attendees:
            attendees = [attendee.to_dict() for attendee in self.attendees]
        return {
            "summary": self.summary,
            "location": self.location,
            "description": self.description,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "recurrence": self.recurrence,
            "attendees": attendees,
            "reminders": self.reminders.to_dict(),
        }


class GoogleCalendar:
    def __init__(self):
        SCOPES = ["https://www.googleapis.com/auth/calendar"]
        token_path = "secrets/token.pickle"
        if os.path.exists(token_path):
            with open(token_path, "rb") as token:
                self.creds = pickle.load(token)
        else:
            logger.error(f"Token file {token_path} not found.")
            raise Exception("Token file not found.")

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                with open(token_path, "wb") as token:
                    pickle.dump(self.creds, token)
            else:
                logger.error("Credentials are invalid and cannot be refreshed")
                raise Exception("Credentials are invalid and cannot be refreshed")

        try:
            self.service = build("calendar", "v3", credentials=self.creds)
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            raise error

    def create_google_calendar_event(self, event: GoogleCalendarEvent) -> str:
        """
        Create a google calendar event for the booking
        :param booking_id: booking id
        :param booking_data: booking data
        :return: None
        """
        try:
            logger.debug(f"Event: {event.to_dict()}")
            event = (
                self.service.events()
                .insert(calendarId="primary", body=event.to_dict())
                .execute()
            )
            logger.info(f'Event created: {event.get("htmlLink")}')
            return event.get("id")
        except HttpError as error:
            logger.error(f"An error occurred: {error}")

    def update_google_calendar_event(self, event_id: str, event: GoogleCalendarEvent):
        """
        Update a google calendar event for the booking
        :param booking_id: booking id
        :param booking_data: booking data
        :return: None
        """
        try:
            logger.debug(f"Event: {event.to_dict()}")
            event = (
                self.service.events()
                .update(calendarId="primary", eventId=event_id, body=event.to_dict())
                .execute()
            )
            logger.info(f'Event updated: {event.get("htmlLink")}')
            return event.get("id")
        except HttpError as error:
            logger.error(f"An error occurred: {error}")

    def delete_google_calendar_event(self, event_id: str):
        """
        Delete a google calendar event for the booking
        :param booking_id: booking id
        :param booking_data: booking data
        :return: None
        """
        try:
            self.service.events().delete(
                calendarId="primary", eventId=event_id
            ).execute()
            logger.info(f"Event deleted: {event_id}")
        except HttpError as error:
            logger.error(f"An error occurred: {error}")


if __name__ == "__main__":
    # Create a Google Calendar object
    google_calendar = GoogleCalendar()
    # Create a event that lasts for one hour and the time zone is Europe/Berlin
    event = GoogleCalendarEvent(
        summary="Test Event",
        location="Online",
        description="This is a test event",
        start=EventTime(datetime.now(), "Europe/Berlin"),
        end=EventTime(datetime.now() + timedelta(hours=1), "Europe/Berlin"),
        recurrence=["RRULE:FREQ=DAILY;COUNT=2"],
        attendees=[EventAttendee("test@example.com")],
        reminders=EventReminder(
            useDefault=False, overrides=[EventReminderOverride("email", 10)]
        ),
    )

    created_event = google_calendar.create_google_calendar_event(event)
    time.sleep(5)
    google_calendar.delete_google_calendar_event(created_event)
