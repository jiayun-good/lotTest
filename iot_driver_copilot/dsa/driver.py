import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DEVICE_NAME = os.environ.get("DEVICE_NAME", "dsa")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "dsa")
MANUFACTURER = os.environ.get("MANUFACTURER", "")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

class SimpleDeviceDriver(BaseHTTPRequestHandler):
    def _set_json_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_json_headers()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": MANUFACTURER
            }
            self.wfile.write(json.dumps(info).encode('utf-8'))
        elif self.path == '/health':
            # Health check: always 'ok' for this static driver
            self._set_json_headers()
            health = {
                "status": "ok",
                "reachable": True
            }
            self.wfile.write(json.dumps(health).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "Not found"}')

def run():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, SimpleDeviceDriver)
    httpd.serve_forever()

if __name__ == "__main__":
    run()