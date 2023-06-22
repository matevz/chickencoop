import RPi.GPIO as GPIO

from config import MANUAL_DOOR_BUTTON_PIN


def init_manual_door_button(callback):
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(MANUAL_DOOR_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	GPIO.add_event_detect(MANUAL_DOOR_BUTTON_PIN, GPIO.RISING, callback=callback)
