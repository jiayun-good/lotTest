import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

DEVICE_NAME = os.environ.get("DEVICE_NAME", "sasdds")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "sasdds")
MANUFACTURER = os.environ.get("MANUFACTURER", "")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "")

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

class SimpleDeviceHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self._set_headers()
            resp = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": MANUFACTURER,
                "device_type": DEVICE_TYPE,
            }
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "not found"}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''
            try:
                data = json.loads(body.decode())
            except Exception:
                data = {}
            # Since device has no real commands, just echo back
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "success",
                "received": data
            }).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "not found"}).encode('utf-8'))

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), SimpleDeviceHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
