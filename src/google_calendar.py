import logging
logger = logging.getLogger("google_calendar")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler("app-google-calendar.log")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


