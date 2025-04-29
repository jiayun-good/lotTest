import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

DEVICE_INFO = {
    "device_name": "dassad",
    "device_model": "das",
    "manufacturer": "sad",
    "device_type": "sad"
}

HTTP_HOST = os.environ.get("HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.environ.get("HTTP_PORT", "8080"))

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/info":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

def run(server_class=HTTPServer, handler_class=DeviceHTTPRequestHandler):
    server_address = (HTTP_HOST, HTTP_PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()