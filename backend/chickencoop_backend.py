#!/usr/bin/python

import json
import dataclasses
from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import RPi.GPIO as GPIO

from datetime import datetime, timezone
import config
from status import Status
import manual_door
import temperature

HOSTNAME = ''
PORT = 1234

status: Status


class ChickenCoopHTTPHandler(BaseHTTPRequestHandler):

	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
	
	def do_GET(s):
		global status
		s.send_response(200)
		logging.info(s.path)

		# Backend returns JSON only.
		s.send_header("Content-type", "application/json")
		s.end_headers()

		if s.path.startswith("/status"):
			(avgH, avgT) = temperature.compute_avg_humid_temp()
			status.humidity = avgH
			status.temperature = avgT
			status.current_datetime = datetime.now(timezone.utc)
			s.wfile.write(json.dumps(dataclasses.asdict(status), default=str).encode())
		elif s.path.startswith("/door_down"):
			status.door = False
			config.save_cfg_from_status(status)
			update_gpio()
		elif s.path.startswith("/door_up"):
			status.door = True
			config.save_cfg_from_status(status)
			update_gpio()
		elif s.path.startswith("/light_on"):
			status.light = True
			config.save_cfg_from_status(status)
			update_gpio()
		elif s.path.startswith("/light_off"):
			status.light = False
			config.save_cfg_from_status(status)
			update_gpio()
		else:
			s.send_response(404)


def init_gpio():
	GPIO.cleanup()
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(config.DOOR_SWITCH_PIN, GPIO.OUT)
	GPIO.setup(config.LIGHT_SWITCH_PIN, GPIO.OUT)
	GPIO.setup(config.MASTER_SWITCH_PIN, GPIO.OUT)


def update_gpio():
	global status

	logging.info(f'Updating GPIOs: {status}')

	GPIO.output(config.DOOR_SWITCH_PIN, status.door)
	GPIO.output(config.LIGHT_SWITCH_PIN, status.light)
	GPIO.output(config.MASTER_SWITCH_PIN, status.master)


def switch_door():
	global status

	logging.info('Switching door direction %d -> %d', status.door, not status.door)
	status.door = not status.door
	status.last_manual_door_datetime = datetime.now(timezone.utc)
	config.save_cfg_from_status(status)
	update_gpio()


if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG)
	init_gpio()
	manual_door.init_manual_door_service(switch_door)
	temperature.init_temperature_service()

	status = config.load_cfg_to_status()
	update_gpio()

	httpd = HTTPServer((HOSTNAME, PORT), ChickenCoopHTTPHandler)
	logging.info(f'Chicken Coop Backend listening on {HOSTNAME}:{PORT}')
	try:
		httpd.serve_forever()
	except:
		pass
	httpd.server_close()
	temperature.stop_temperature_service()
	manual_door.stop_manual_door_service()
	GPIO.cleanup()
	logging.info('Server stopped - keyboard interrupt')
