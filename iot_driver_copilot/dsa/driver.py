import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DEVICE_INFO = {
    "device_name": os.environ.get("DEVICE_NAME", "dsa"),
    "device_model": os.environ.get("DEVICE_MODEL", "dsa"),
    "manufacturer": os.environ.get("DEVICE_MANUFACTURER", ""),
    "device_type": os.environ.get("DEVICE_TYPE", "")
}

class DeviceHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode())
        elif self.path == "/health":
            self._set_headers()
            health = {"status": "online"}
            self.wfile.write(json.dumps(health).encode())
        else:
            self._set_headers(status=404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run():
    server_host = os.environ.get("SERVER_HOST", "0.0.0.0")
    server_port = int(os.environ.get("SERVER_PORT", "8080"))
    httpd = HTTPServer((server_host, server_port), DeviceHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run()