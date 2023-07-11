#!/usr/bin/python

import dataclasses
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import RPi.GPIO as GPIO
from urllib.parse import parse_qs

import config
from status import Status
import manual_door
import schedule
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
		elif s.path.startswith("/door_open"):
			door_open()
		elif s.path.startswith("/door_close"):
			door_close()
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

	def do_POST(s):
		content_length = int(s.headers['Content-Length'])
		post_raw = s.rfile.read(content_length)
		post = parse_qs(post_raw.decode(), strict_parsing=True)
		print(post_raw)
		print(post)
		if "action" in post and len(post["action"])==1:
			if post["action"][0] == "apply_schedule":
				status.schedule_city = post["schedule_city"][0]
				status.schedule_door_open = ("schedule_door_open" in post)
				status.schedule_door_close = ("schedule_door_close" in post)
				status.schedule_door_open_offset = int(post["schedule_door_open_offset"][0])
				status.schedule_door_close_offset = int(post["schedule_door_close_offset"][0])
				config.save_cfg_from_status(status)
				schedule.reset_today_state()

		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()

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


def door_open():
	global status
	status.door = True
	config.save_cfg_from_status(status)
	update_gpio()


def door_close():
	global status
	status.door = False
	config.save_cfg_from_status(status)
	update_gpio()


def switch_door():
	global status

	logging.info('Switching door direction %d -> %d', status.door, not status.door)
	status.door = not status.door
	status.last_manual_door_datetime = datetime.now(timezone.utc)
	config.save_cfg_from_status(status)
	update_gpio()


if __name__ == '__main__':
	status = config.load_cfg_to_status()

	logging.basicConfig(level=logging.DEBUG)
	init_gpio()
	manual_door.init_manual_door_service(switch_door)
	temperature.init_temperature_service()
	schedule.init_schedule_service(door_open, door_close, status)

	update_gpio()

	httpd = HTTPServer((HOSTNAME, PORT), ChickenCoopHTTPHandler)
	logging.info(f'Chicken Coop Backend listening on {HOSTNAME}:{PORT}')
	try:
		httpd.serve_forever()
	except:
		pass
	httpd.server_close()
	schedule.stop_schedule_service()
	temperature.stop_temperature_service()
	manual_door.stop_manual_door_service()
	GPIO.output(config.MASTER_SWITCH_PIN, False)
	GPIO.cleanup()
	logging.info('Server stopped - keyboard interrupt')
