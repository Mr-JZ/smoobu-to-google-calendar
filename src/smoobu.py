from dataclasses import dataclass
from dotenv import load_dotenv
from datetime import datetime
import os
import requests
import logging

# how to import List
from typing import List

load_dotenv()

logger = logging.getLogger("smoobu")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app-smoobu.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


@dataclass
class Apartment:
    id: int
    name: str

    @staticmethod
    def from_json(json_data):
        return Apartment(json_data["id"], json_data["name"])


@dataclass
class Channel:
    id: int
    name: str

    @staticmethod
    def from_json(json_data):
        return Channel(json_data["id"], json_data["name"])


@dataclass
class Booking:
    id: int
    reference_id: str
    type: str
    arrival: datetime
    departure: datetime
    created_at: datetime
    modified_at: datetime
    apartment: Apartment
    channel: Channel
    guest_name: str
    email: str
    phone: str
    adults: int
    children: int
    check_in: str
    check_out: str
    notice: str
    price: int
    price_paid: str
    prepayment: int
    prepayment_paid: str
    deposit: int
    deposit_paid: str
    language: str
    guest_app_url: str
    is_blocked_booking: bool
    guest_id: int
    related: List[Apartment]

    @staticmethod
    def from_json(json_data):
        return Booking(
            json_data["id"],
            json_data["reference-id"],
            json_data["type"],
            datetime.strptime(json_data["arrival"], "%Y-%m-%d"),
            datetime.strptime(json_data["departure"], "%Y-%m-%d"),
            datetime.strptime(json_data["created-at"], "%Y-%m-%d %H:%M"),
            datetime.strptime(json_data["modifiedAt"], "%Y-%m-%d %H:%M:%S"),
            Apartment.from_json(json_data["apartment"]),
            Channel.from_json(json_data["channel"]),
            json_data["guest-name"],
            json_data["email"],
            json_data["phone"],
            json_data["adults"],
            json_data["children"],
            json_data["check-in"],
            json_data["check-out"],
            json_data["notice"],
            json_data["price"],
            json_data["price-paid"],
            json_data["prepayment"],
            json_data["prepayment-paid"],
            json_data["deposit"],
            json_data["deposit-paid"],
            json_data["language"],
            json_data["guest-app-url"],
            json_data["is-blocked-booking"],
            json_data["guestId"],
            [Apartment.from_json(related) for related in json_data["related"]],
        )


@dataclass
class BookingList:
    page_count: int
    page_size: int
    total_items: int
    page: int
    bookings: List[Booking]

    @staticmethod
    def from_json(json_data):
        return BookingList(
            json_data["page_count"],
            json_data["page_size"],
            json_data["total_items"],
            json_data["page"],
            [Booking.from_json(booking) for booking in json_data["bookings"]],
        )


class Smoobu:
    def __init__(self):
        self.api_key = os.getenv("SMOOBU_API")
        self.headers = {"Api-Key": self.api_key, "Cache-Control": "no-cache"}

    def get_smoobu_reservations(self) -> List[Booking]:
        """
        Get the data from smoobu api
        :return: list of dict
        """
        response = requests.get(
            "https://login.smoobu.com/api/reservations",
            headers=self.headers,
        )
        data = response.json()
        booking_list = BookingList.from_json(data)
        # make a function that goes through the pages and gets all the bookings
        bookings = booking_list.bookings
        for page in range(1, booking_list.page_count):
            response = requests.get(
                f"https://login.smoobu.com/api/reservations?page={page}",
                headers=self.headers,
            )
            data = response.json()
            booking_list = BookingList.from_json(data)
            bookings.extend(booking_list.bookings)
            logger.debug(f"Page {page} of {booking_list.page_count} loaded")
        if booking_list.total_items > len(bookings):
            logger.warning(
                f"Total bookings: {booking_list.total_items} is greater than the number of bookings returned: {len(bookings)}"
            )
        logger.info(f"Total bookings: {len(bookings)}")
        return bookings


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    smoobu = Smoobu()
    bookings = smoobu.get_smoobu_reservations()
