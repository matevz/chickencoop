import RPi.GPIO as GPIO

from config import MANUAL_DOOR_BUTTON_PIN


def init_manual_door_button(callback):
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(MANUAL_DOOR_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(MANUAL_DOOR_BUTTON_PIN, GPIO.FALLING, callback=callback, bouncetime=2000)
