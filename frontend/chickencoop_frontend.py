#!/usr/bin/python

from datetime import datetime
from http.server import BaseHTTPRequestHandler,HTTPServer
import logging
import requests
import socketserver
import sys
from urllib.parse import parse_qs

from camera import output, init_camera

# Import backend
sys.path.append('../backend')

HOSTNAME = ''
PORT = 8080

BACKEND_HOSTNAME = 'localhost'
BACKEND_PORT = 1234

HTML_PATH_INDEX='./index.phtml'
SCRIPT_PATH='./script.js'

class ChickenCoopHTTPHandler(BaseHTTPRequestHandler):

	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
	
	def do_GET(self):
		if self.path == '/stream.mjpg':
			self.send_response(200)
			self.send_header('Age', 0)
			self.send_header('Cache-Control', 'no-cache, private')
			self.send_header('Pragma', 'no-cache')
			self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
			self.end_headers()
			try:
				while True:
					with output.condition:
						output.condition.wait()
						frame = output.frame
					self.wfile.write(b'--FRAME\r\n')
					self.send_header('Content-Type', 'image/jpeg')
					self.send_header('Content-Length', len(frame))
					self.end_headers()
					self.wfile.write(frame)
					self.wfile.write(b'\r\n')
			except Exception as e:
				logging.warning(f'removed streaming client {self.client_address}: {e}')
		if self.path == '/status':
			self.send_response(200)
			self.send_header("Content-type", "text/json")
			self.end_headers()

			status_url = "http://{host}:{port}/status".format(host=BACKEND_HOSTNAME, port=BACKEND_PORT)
			r = requests.get(url=status_url)
			self.wfile.write(r.content)
		else:
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

			sf = open(SCRIPT_PATH, 'r')
			script = sf.read()
			sf.close()

			f = open(HTML_PATH_INDEX)
			self.wfile.write(f.read().format(SCRIPT=script).encode())
			f.close()

	def do_POST(s):
		content_length = int(s.headers['Content-Length'])
		post_raw = s.rfile.read(content_length)
		post = parse_qs(post_raw.decode(), strict_parsing=True)
		if "action" in post and len(post["action"])==1:
			if post["action"][0] in ["door_open", "door_close", "light_on", "light_off"]:
				url = "http://{host}:{port}/{path}".format(host=BACKEND_HOSTNAME, port=BACKEND_PORT, path=post["action"][0])
				requests.get(url)
			elif post["action"][0] in ["apply_schedule"]:
				url = "http://{host}:{port}/{path}".format(host=BACKEND_HOSTNAME, port=BACKEND_PORT, path=post["action"][0])
				requests.post(url, post)

		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, HTTPServer):
	allow_reuse_address = True
	daemon_threads = True


logging.basicConfig(level=logging.DEBUG)
init_camera()
httpd = StreamingServer((HOSTNAME, PORT), ChickenCoopHTTPHandler)
logging.info(f'Chicken Coop Frontend listening on {HOSTNAME}:{PORT}. Connecting to Backend service on {BACKEND_HOSTNAME}:{BACKEND_PORT}')
try:
	httpd.serve_forever()
except:
	pass
httpd.server_close()
logging.info('Server stopped - keyboard interrupt')
