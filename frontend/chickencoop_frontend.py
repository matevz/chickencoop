#!/usr/bin/python

from datetime import datetime
from http.server import BaseHTTPRequestHandler,HTTPServer
import requests
import sys
from urllib.parse import parse_qs

# Import backend
sys.path.append('../')
from backend.chickencoop_backend import HOSTNAME as BACKEND_HOSTNAME
from backend.chickencoop_backend import PORT as BACKEND_PORT
from backend.status import Status

HOSTNAME = ''
PORT = 80

HTML_PATH_INDEX='./index.phtml'

class TempHTTPHandler(BaseHTTPRequestHandler):
	
	def do_HEAD(s):
		s.send_response(200)
		s.send_header("Content-type", "application/json")
		s.end_headers()
	
	def do_GET(s):
		s.send_response(200)
		s.send_header("Content-type", "text/html")
		s.end_headers()

		status_url = "http://{host}:{port}/status".format(host=BACKEND_HOSTNAME, port=BACKEND_PORT)

		# sending get request and saving the response as response object
		r = requests.get(url=status_url)
		status = Status(**r.json())

		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		f = open(HTML_PATH_INDEX)
		s.wfile.write(f.read().format(
			T=status.temperature,
			H=status.hum,
			TIMESTAMP=timestamp,
			DOOR="Odprta" if status.door==True else "Zaprta",
			LIGHT="Prižgana" if status.light==True else "Ugasnjena",
			).encode()
		)
		f.close()

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_raw = self.rfile.read(content_length)
		post = parse_qs(post_raw.decode(), strict_parsing=True)
		if post["submit"] in ["door_up", "door_down", "light_on", "light_off"]:
			url = "http://{host}:{port}/{path}".format(host=BACKEND_HOSTNAME, port=BACKEND_PORT, path=post["submit"])
			requests.get(url)

		self.send_response(302)
		self.send_header('Location', '/')
		self.end_headers()

httpd = HTTPServer((HOSTNAME, PORT), TempHTTPHandler)
print("Chicken Coop Frontend listening on "+HOSTNAME+":"+str(PORT))
try:
	httpd.serve_forever()
except:
	pass
httpd.server_close()
print("Server stopped - keyboard interrupt")
