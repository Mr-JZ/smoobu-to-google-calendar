import logging
import os
from typing import List
from smoobu import Smoobu, Booking
from google_calendar import (
    GoogleCalendarEvent,
    EventTime,
    EventAttendee,
    EventReminder,
    EventReminderOverride,
    GoogleCalendar,
)
from database import Db

logger = logging.getLogger("main")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app-main.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def create_calendar_event(booking: Booking):
    event = GoogleCalendarEvent(
        summary=f"[{booking.reference_id}] {booking.guest_name}",
        location=booking.apartment.name,
        description=f"""
        {booking.check_out}
        Name: {booking.guest_name}
        send message: {booking.guest_app_url}
        """,
        start=EventTime(booking.arrival),
        end=EventTime(booking.departure),
    )
    return event

def create_and_insert_google_calendar_events(bookings: List[Booking], db: Db):
    """
    Create and insert google calendar events to the database
    :param bookings: list of bookings
    :return: None
    """
    google_calendar = GoogleCalendar()
    for booking in bookings:
        event = create_calendar_event(booking)
        event_id = google_calendar.create_google_calendar_event(event)
        if event_id is None:
            return
        db.insert_google_calendar_event(booking, event_id)


def delete_google_calendar_events(bookings: List[GoogleCalendarEvent], db: Db):
    """
    Delete the google calendar events from the database
    :param bookings: list of bookings
    :return: None
    """
    google_calendar = GoogleCalendar()
    for booking in bookings:
        # google_calendar.delete_google_calendar_event(booking.id)
        db.delete_google_calendar_event(booking.id)

def check_modified_bookings(bookings: List[Booking], db: Db):
    """
    Check if the bookings are modified in the database
    :param bookings: list of bookings
    :return: None
    """
    google_calendar = GoogleCalendar()
    with Db() as db:
        for booking in bookings:
            calender_event_id = db.is_modified(booking.id, booking.modified_at)
            if calender_event_id:
                event = create_calendar_event(booking)
                google_calendar.update_google_calendar_event(
                    calender_event_id[0], event
                )
                db.update_modified_at(booking.id, booking.modified_at)
                print(f"Booking {calender_event_id[0]} is modified")
                logger.info(f"Booking {booking.id} is modified")



def sync_smoobu_to_google_calendar():
    logger.info("Starting the sync")
    bookings = Smoobu().get_smoobu_reservations()
    with Db() as db:
        (
            database_events_not_in_bookings,
            bookings_not_in_database_events,
        ) = db.get_entries_not_in_list(bookings)
        logger.debug(f"Number of bookings not in the database: {len(bookings_not_in_database_events)}")
        logger.debug(f"Number of database events not in bookings: {len(database_events_not_in_bookings)}")
        if bookings_not_in_database_events:
            create_and_insert_google_calendar_events(
                bookings_not_in_database_events, db
            )
        if database_events_not_in_bookings:
            delete_google_calendar_events(database_events_not_in_bookings, db)
        check_modified_bookings(bookings, db)


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    sync_smoobu_to_google_calendar()
