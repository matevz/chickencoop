#!/usr/bin/python

from datetime import datetime
from http.server import BaseHTTPRequestHandler,HTTPServer
import requests
import socketserver
import sys
from urllib.parse import parse_qs

from camera import output, init_camera

# Import backend
sys.path.append('../backend')
from status import Status

HOSTNAME = ''
PORT = 8080

BACKEND_HOSTNAME = 'localhost'
BACKEND_PORT = 1234

HTML_PATH_INDEX='./index.phtml'

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
				print("Warning: Removed streaming client {0}: {1}".format(self.client_address, str(e)))
		else:
			self.send_response(200)
			self.send_header("Content-type", "text/html")
			self.end_headers()

			status_url = "http://{host}:{port}/status".format(host=BACKEND_HOSTNAME, port=BACKEND_PORT)

			# sending get request and saving the response as response object
			r = requests.get(url=status_url)
			print(r.json())
			status = Status(**r.json())

			timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			f = open(HTML_PATH_INDEX)
			self.wfile.write(f.read().format(
				T=status.temperature,
				H=status.humidity,
				TIMESTAMP=timestamp,
				MASTER="Vklopljeno" if status.master==True else "Izklopljeno",
				DOOR="Odprta" if status.door==True else "Zaprta",
				LIGHT="Prižgana" if status.light==True else "Ugasnjena",
				).encode()
			)
			f.close()

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_raw = self.rfile.read(content_length)
		post = parse_qs(post_raw.decode(), strict_parsing=True)
		print(post)
		if "action" in post and len(post["action"])==1 and post["action"][0] in ["door_up", "door_down", "light_on", "light_off"]:
			url = "http://{host}:{port}/{path}".format(host=BACKEND_HOSTNAME, port=BACKEND_PORT, path=post["action"][0])
			r = requests.get(url)
			print(r)

		self.send_response(302)
		self.send_header('Location', '/')
		self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, HTTPServer):
	allow_reuse_address = True
	daemon_threads = True


init_camera()
httpd = StreamingServer((HOSTNAME, PORT), ChickenCoopHTTPHandler)
print("Chicken Coop Frontend listening on "+HOSTNAME+":"+str(PORT))
try:
	httpd.serve_forever()
except:
	pass
httpd.server_close()
print("Server stopped - keyboard interrupt")
