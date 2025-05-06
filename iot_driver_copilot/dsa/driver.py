import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import socket

DEVICE_NAME = os.environ.get("DEVICE_NAME", "dsa")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "dsa")
MANUFACTURER = os.environ.get("MANUFACTURER", "")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            response = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": MANUFACTURER
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        elif self.path == "/health":
            self._set_headers()
            # Health: Check if device is reachable (simulate local connectivity)
            status = "ok"
            try:
                # Simulate a health check by resolving localhost, since no device protocol info is available
                socket.gethostbyname(socket.gethostname())
            except Exception:
                status = "unreachable"
            response = {
                "status": status
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_headers(404)
            response = {
                "error": "Not found"
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

def run():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()