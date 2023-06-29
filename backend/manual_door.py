import logging
import RPi.GPIO as GPIO
import threading
import time

from config import MANUAL_DOOR_BUTTON_PIN

# Number of seconds between two consecutive button state checks.
DOOR_SWITCH_SLEEP = 0.1

# Number of required confirmations until the door is actually triggered.
DOOR_SWITCH_THRESHOLD = 35

# Is checking the door active.
DOOR_SWITCH_ENABLED = False

# Main door loop thread.
t: threading.Thread


def init_manual_door_service(callback):
	global DOOR_SWITCH_ENABLED, t

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(MANUAL_DOOR_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	t = threading.Thread(target=read_door, args=[callback])
	DOOR_SWITCH_ENABLED = True
	t.start()


def stop_manual_door_service():
	global DOOR_SWITCH_ENABLED
	DOOR_SWITCH_ENABLED = False
	t.join()


def read_door(callback):
	global DOOR_SWITCH_THRESHOLD, DOOR_SWITCH_SLEEP, DOOR_SWITCH_ENABLED

	counter = 0
	while DOOR_SWITCH_ENABLED:
		if GPIO.input(MANUAL_DOOR_BUTTON_PIN) == GPIO.LOW:
			logging.info('Manual Door Button pressed? Waiting for confirmation... %d/%d', counter, DOOR_SWITCH_THRESHOLD)
			counter += 1
			if counter == DOOR_SWITCH_THRESHOLD:
				callback()
				counter = 0
		else:
			counter = 0

		time.sleep(DOOR_SWITCH_SLEEP)
