import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DEVICE_INFO = {
    "device_name": os.environ.get("DEVICE_NAME", "dsa"),
    "device_model": os.environ.get("DEVICE_MODEL", "dsa"),
    "manufacturer": os.environ.get("MANUFACTURER", ""),
    "device_type": os.environ.get("DEVICE_TYPE", ""),
}

HEALTHY_STATUS = {"status": "online", "message": "Device is reachable"}


class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode())
        elif self.path == "/health":
            # In a real implementation, connectivity checks would go here
            self._set_headers()
            self.wfile.write(json.dumps(HEALTHY_STATUS).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def log_message(self, format, *args):
        return  # Suppress default logging


def run():
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    try:
        port = int(os.environ.get("SERVER_PORT", "8080"))
    except ValueError:
        port = 8080

    httpd = HTTPServer((host, port), DeviceHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
