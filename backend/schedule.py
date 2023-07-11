import astral, astral.geocoder, astral.sun
from datetime import datetime, timedelta, timezone
import logging
import RPi.GPIO as GPIO
import threading
from typing import Any, Dict
import time

from status import Status

from config import MANUAL_DOOR_BUTTON_PIN

# Number of seconds between two schedule checks.
SCHEDULE_SLEEP = 60

# Number of seconds after the door up/down event is still considered.
SCHEDULE_THRESHOLD = 300

# Is checking the schedule service main loop running.
SCHEDULE_ENABLED = False

# Configuration.
status: Status

# Main door loop thread.
t: threading.Thread

# Current astral's sun info, updated regularly by the main loop.
sun: Dict[str, Any]

# Status for today.
today_date = datetime.min
today_door_opened = False
today_door_closed = False


def init_schedule_service(door_open_callback, door_close_callback, s):
	global SCHEDULE_ENABLED, t, status
	status = s

	t = threading.Thread(target=check_time, args=[door_open_callback, door_close_callback])
	SCHEDULE_ENABLED = True
	t.start()


def stop_schedule_service():
	global SCHEDULE_ENABLED
	SCHEDULE_ENABLED = False
	t.join()


def check_time(door_open_callback, door_close_callback):
	global status, SCHEDULE_SLEEP, SCHEDULE_THRESHOLD, SCHEDULE_ENABLED, sun, today_date, today_door_opened, today_door_closed

	reset_today_state()

	while SCHEDULE_ENABLED:
		if today_date != datetime.now().date():
			reset_today_state()

		city = astral.geocoder.lookup("London", astral.geocoder.database())
		try:
			city = astral.geocoder.lookup("London" if status.schedule_city == "" else status.schedule_city,
										  astral.geocoder.database())
		except KeyError:


		sun = astral.sun.sun(city.observer)
		status.schedule_sunrise = sun['sunrise']
		status.schedule_sunset = sun['sunset']

		opening_time = sun['sunrise'] + timedelta(minutes=status.schedule_door_open_offset)
		closing_time = sun['sunset'] + timedelta(minutes=status.schedule_door_close_offset)

		logging.info(f'schedule: now {datetime.now()}')
		logging.info(f'schedule: city: {city}, sun: {sun}')
		logging.info(f'schedule: opening_time {opening_time}, closing_time {closing_time}')
		logging.info(f'schedule: opening_time + threshold: {opening_time + timedelta(seconds=SCHEDULE_THRESHOLD)}, closing_time + threshold: {closing_time + timedelta(seconds=SCHEDULE_THRESHOLD)}')
		logging.info(f'schedule: today_door_opened {today_door_opened}, today_door_closed {today_door_closed}')
		logging.info(f'schedule: schedule_door_open {status.schedule_door_open}, schedule_door_close {status.schedule_door_close}')

		if not today_door_opened and status.schedule_door_open and opening_time < datetime.now(timezone.utc) < opening_time + timedelta(seconds=SCHEDULE_THRESHOLD):
			logging.info("Door open schedule event! Good morning 🌅")
			door_open_callback()
			today_door_opened = True

		if not today_door_closed and status.schedule_door_close and closing_time < datetime.now(timezone.utc) < closing_time + timedelta(seconds=SCHEDULE_THRESHOLD):
			logging.info("Door close schedule event! Good night 🌇")
			door_close_callback()
			today_door_closed = True

		time.sleep(SCHEDULE_SLEEP)


def reset_today_state():
	global today_date, today_door_opened, today_door_closed

	logging.info(f'schedule: resetting today state, old values: {today_date}, {today_door_opened}, {today_door_closed}')
	today_date = datetime.now().date()
	today_door_opened = False
	today_door_closed = False
