import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Mock device: Simulate device communication for demo
class TttDeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_data_points(self):
        # Simulate a device data fetch, e.g., via TCP socket or custom protocol
        # Replace with actual communication logic as needed
        return {
            "temperature": 25.3,
            "humidity": 48.7,
            "status": "OK"
        }

    def send_command(self, cmd_payload):
        # Simulate command send; parse and respond
        if cmd_payload.get('action') == 'reset':
            return {"result": "Device reset"}
        elif cmd_payload.get('action') == 'ping':
            return {"result": "pong"}
        else:
            return {"result": "Unknown command", "error": True}

device_client = TttDeviceClient(DEVICE_IP, DEVICE_PORT)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            data = device_client.get_data_points()
            self._set_headers()
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
                payload = json.loads(post_data.decode('utf-8'))
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                return
            result = device_client.send_command(payload)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=Handler):
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = server_class(server_address, handler_class)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()