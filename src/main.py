import os
import requests
import sqlite3
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def get_smoobu_data():
    """
    Get the data from smoobu api
    :return: list of dict
    """
    url = f"https://api.smoobu.com/v1/customers?api_key={os.getenv('SMOOBU_API')}"
    response = requests.get(url)
    data = response.json()
    return data


if __name__ == "__main__":
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()
    # Create a table for the google calendar events to the booking id from the smoobu api
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS google_calendar_events (
            booking_id TEXT PRIMARY KEY,
            event_id TEXT,
            event_title TEXT,
            event_start TEXT,
            event_end TEXT
        )
        """
    )
    conn.commit()
    # Get the data from smoobu api
    smoobu_data = get_smoobu_data()
    print(smoobu_data)



