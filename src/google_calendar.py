from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import List
import pickle
import os
import json
import logging
import time

logger = logging.getLogger("google_calendar")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app-google-calendar.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


@dataclass
class EventTime:
    dateTime: datetime
    timeZone: str

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
    recurrence: List[str]
    attendees: List[EventAttendee]
    reminders: EventReminder

    def to_dict(self):
        return {
            "summary": self.summary,
            "location": self.location,
            "description": self.description,
            "start": self.start.to_dict(),
            "end": self.end.to_dict(),
            "recurrence": self.recurrence,
            "attendees": [attendee.to_dict() for attendee in self.attendees],
            "reminders": self.reminders.to_dict(),
        }


