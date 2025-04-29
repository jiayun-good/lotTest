import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))

# Mock device communication
def fetch_device_data():
    # Simulate retrieving data from the device over the proprietary protocol
    # In a real scenario, this would involve a socket connection or protocol-specific logic
    return {
        "temperature": 22.5,
        "humidity": 55,
        "status": "ok"
    }

def send_device_command(cmd_payload):
    # Simulate sending a command to the device over the proprietary protocol
    # In a real scenario, this would involve a socket connection or protocol-specific logic
    return {
        "result": "success",
        "echo": cmd_payload
    }

class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_json_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/data':
            data = fetch_device_data()
            self._set_json_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            length = int(self.headers.get('content-length', 0))
            post_data = self.rfile.read(length)
            try:
                cmd_payload = json.loads(post_data.decode('utf-8'))
            except Exception:
                self._set_json_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                return
            result = send_device_command(cmd_payload)
            self._set_json_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, IoTDeviceHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
