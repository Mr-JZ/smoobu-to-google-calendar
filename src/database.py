import sqlite3
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
from smoobu import Booking, BookingList
from google_calendar import GoogleCalendarEvent
from smoobu import Smoobu
from google_calendar import GoogleCalendar

logger = logging.getLogger("database")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app-database.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

debug = False


@dataclass
class GoogleCalendarEvent:
    booking_id: int
    booking_modified_at: datetime
    event_id: str


class Db:
    def __init__(self):
        try:
            self.conn = sqlite3.connect("data.db")
            self.cursor = self.conn.cursor()
            logger.info("Database connected")
        except sqlite3.Error as error:
            logger.error(f"An error occurred: {error}")
        # Create a table for the google calendar events to the booking id from the smoobu api
        try:
            if debug:
                query = """
                    CREATE TABLE IF NOT EXISTS google_calendar_events (
                        booking_id INTEGER PRIMARY KEY NOT NULL,
                        booking_modified_at DATETIME NOT NULL,
                        event_id TEXT NULL
                    )
                    """
                self.cursor.execute("DROP TABLE IF EXISTS google_calendar_events")
            else:
                query = """
                    CREATE TABLE IF NOT EXISTS google_calendar_events (
                        booking_id INTEGER PRIMARY KEY,
                        booking_modified_at TEXT,
                        event_id TEXT NOT NULL
                    )
                    """
            self.cursor.execute(query)
            self.conn.commit()
        except sqlite3.IntegrityError as error:
            logger.error(f"An error occurred: {error}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the runtime context and close the database connection."""
        try:
            self.cursor.close()
            self.conn.close()
            logger.info("Database connection closed")
        except sqlite3.Error as error:
            logger.error(f"Failed to close the database connection: {error}")

    
    def insert_google_calendar_event(self, booking: Booking, event: str):
        """
        Insert a google calendar event to the database
        :param booking: booking data
        :return: None
        """
        try:
            # Assuming booking.modified_at is a datetime object, convert to a string if needed
            modified_at_str = booking.modified_at.strftime('%Y-%m-%d %H:%M:%S')
            logger.debug(f"Booking Id: {booking.id}\nModified at: {modified_at_str}\nEvent Id: {event}")
            self.cursor.execute(
                f"""
                INSERT INTO google_calendar_events (booking_id, booking_modified_at, event_id)
                VALUES ({booking.id}, '{modified_at_str}', '{event}')
                """
            )
            logger.debug(f"Event inserted: {booking.id}")
            self.conn.commit()
        except sqlite3.IntegrityError as error:
            logger.error(f"An error occurred: {error} with booking id: {booking.id}")
        except sqlite3.InterfaceError as error:
            logger.error(f"Interface error occurred: {error} with booking id: {booking.id}")


    def delete_google_calendar_event(self, booking_id: int):
        """
        Delete a google calendar event from the database
        :param booking_id: booking id
        :return: None
        """
        try:
            self.cursor.execute(
                """
                DELETE FROM google_calendar_events
                WHERE booking_id = ?
                """,
                (booking_id,),
            )
            logger.debug(f"Event deleted: {booking_id}")
            self.conn.commit()
        except sqlite3.Error as error:
            logger.error(f"An error occurred: {error}")

    def is_modified(self, booking_id: str, booking_modified_at: datetime):
        """
        Check if the booking is modified
        :param booking_id: booking id
        :param booking_modified_at: booking modified at
        :return: True if modified, False otherwise
        """
        try:
            modified_at_str = booking_modified_at.strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                f"""
                SELECT event_id FROM google_calendar_events
                WHERE booking_id = '{booking_id}' AND booking_modified_at != '{modified_at_str}'
                """,
            )
            result = self.cursor.fetchone()
            return result
        except sqlite3.Error as error:
            logger.error(f"An error occurred: {error}")

    def update_modified_at(self, booking_id: str, booking_modified_at: datetime):
        """
        Update the modified_at field in the database
        :param booking_id: booking id
        :param booking_modified_at: booking modified at
        :return: None
        """
        try:
            modified_at_str = booking_modified_at.strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute(
                f"""
                UPDATE google_calendar_events
                SET booking_modified_at = '{modified_at_str}'
                WHERE booking_id = '{booking_id}'
                """
            )
            logger.debug(f"Modified at updated: {booking_id}")
            self.conn.commit()
        except sqlite3.Error as error:
            logger.error(f"An error occurred: {error}")

    def get_all(self):
        """
        Get all the google calendar events from the database
        :return: list of GoogleCalendarEvent
        """
        self.cursor.execute(
            """
            SELECT * FROM google_calendar_events
            """
        )
        return self.cursor.fetchall()

    def get_entries_not_in_list(
        self, bookings: List[Booking]
    ) -> Tuple[List[GoogleCalendarEvent], List[Booking]]:
        """
        Get all the google calendar events from the database that are not in the bookings list,
        and bookings that are not in the database.

        :return: tuple (events_not_in_bookings, bookings_not_in_database)
        """
        try:
            if not bookings:
                query = "SELECT * FROM google_calendar_events"
                self.cursor.execute(query)
                results = self.cursor.fetchall()
                logger.debug(f"Total events: {len(results)}")
                return results, []
            else:
                # Get booking IDs from the list of bookings
                booking_ids = [booking.id for booking in bookings]

                placeholders = ", ".join(["?"] * len(booking_ids))
                query = f"SELECT * FROM google_calendar_events WHERE booking_id NOT IN ({placeholders})"
                self.cursor.execute(query, booking_ids)
                database_events_not_in_bookings = self.cursor.fetchall()
                logger.debug(
                    f"Total database events not in bookings: {len(database_events_not_in_bookings)}"
                )

                # Now, find bookings that are not in the database
                query = "SELECT booking_id FROM google_calendar_events"
                self.cursor.execute(query)
                existing_booking_ids = {row[0] for row in self.cursor.fetchall()}
                logger.debug(f"The booking ids in the database: {existing_booking_ids}")

                bookings_not_in_database = [
                    booking
                    for booking in bookings
                    if booking.id not in existing_booking_ids
                ]
                logger.debug(
                    f"The bookings not in the database: {[booking.id for booking in bookings_not_in_database]}"
                )

                return database_events_not_in_bookings, bookings_not_in_database
        except sqlite3.Error as error:
            logger.error(f"get_entries_not_in_list: {error}")
            return [], []

    def delete_google_calendar_entries(self):
        """
        Delete all the google calendar entries from the database
        :return: None
        """
        try:
            # Get all the entries from the database but only the event_id
            self.cursor.execute(
                """
                SELECT event_id FROM google_calendar_events
                """
            )
            entries_to_delete = [row[0] for row in self.cursor.fetchall()]
            google_calendar = GoogleCalendar()
            for entry in entries_to_delete:
                google_calendar.delete_google_calendar_event(entry)
            self.conn.commit()
        except sqlite3.Error as error:
            logger.error(f"An error occurred: {error}")


if __name__ == "__main__":
    with Db() as db:
        db.delete_google_calendar_entries()
