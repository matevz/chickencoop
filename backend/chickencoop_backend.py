#!/usr/bin/python

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import RPi.GPIO as GPIO

from datetime import datetime
import config
from status import Status
import manual_door
import temperature

HOSTNAME = ''
PORT = 1234

status = Status()

class ChickenCoopHTTPHandler(BaseHTTPRequestHandler):

	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
	
	def do_GET(s):
		global status
		s.send_response(200)
		if (s.path.startswith("/status")):
			# return JSON result
			s.send_header("Content-type", "application/json")
			s.end_headers()
			
			(avgH, avgT) = temperature.compute_avg_humid_temp()
			status.humidity = avgH
			status.temperature = avgT
			s.wfile.write(json.dumps(status).encode())
		elif (s.path.startswith("/door_down")):
			status.door = False
			config.save_cfg_from_status(status)
			update_gpio()
		elif (s.path.startswith("/door_down")):
			status.door = True
			config.save_cfg_from_status(status)
			update_gpio()
		elif (s.path.startswith("/light_on")):
			status.light = True
			config.save_cfg_from_status(status)
			update_gpio()
		elif (s.path.startswith("/light_off")):
			status.light = False
			config.save_cfg_from_status(status)
			update_gpio()


def update_gpio():
	global status

	print("Updating GPIOs: {status}".format(status=status))

	GPIO.output(config.DOOR_SWITCH_PIN, status.door)
	GPIO.output(config.LIGHT_SWITCH_PIN, status.light)
	GPIO.output(config.MASTER_SWITCH_PIN, status.master)


def manual_door_button_callback(channel):
	global status
	if (datetime.now() - status.last_manual_door_datetime).seconds > 2:
		status.door = not status.door
		config.save_cfg_from_status(status)
		update_gpio()
		status.last_manual_door_datetime = datetime.now()


manual_door.init_manual_door_button(manual_door_button_callback)
temperature.init_temperature_service()
status = config.load_cfg_to_status()
update_gpio()

httpd = HTTPServer((HOSTNAME, PORT), ChickenCoopHTTPHandler)
print("Chicken Coop Backend listening on "+HOSTNAME+":"+str(PORT))
try:
	httpd.serve_forever()
except:
	pass
httpd.server_close()
temperature.stop_temperature_service()
GPIO.cleanup()
print("Server stopped - keyboard interrupt")
