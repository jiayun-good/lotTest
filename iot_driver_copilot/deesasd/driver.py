import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse
import threading

# Mock device communication backend for demonstration purposes

class DeviceConnection:
    def __init__(self, ip):
        self.ip = ip

    def send_command(self, command_payload):
        # Simulate sending a command to the device and getting a response
        # Replace with real device communication logic for actual use
        return {
            "status": "success",
            "sent_command": command_payload,
            "device_ip": self.ip
        }

    def get_data(self):
        # Simulate retrieving data points from the device
        # Replace with real device communication logic for actual use
        return {
            "temperature": 23.5,
            "humidity": 45.1,
            "device_ip": self.ip
        }

# Environment variable configuration
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

device_conn = DeviceConnection(DEVICE_IP)

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            self._set_headers()
            data = device_conn.get_data()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data)
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                return
            resp = device_conn.send_command(payload)
            self._set_headers()
            self.wfile.write(json.dumps(resp).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def log_message(self, format, *args):
        # Suppress default HTTP server logging
        return

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Starting deesasd device driver HTTP server at http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()