import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

# Device Info (static for this example, but could come from device queries)
DEVICE_INFO = {
    "device_name": "asd",
    "device_model": "sda",
    "manufacturer": "sad",
    "device_type": "asd"
}

# Dummy device data (for CSV endpoint)
DUMMY_DATA = [
    {"timestamp": "2024-06-10T01:00:00Z", "param1": "123", "param2": "456"},
    {"timestamp": "2024-06-10T01:01:00Z", "param1": "124", "param2": "457"},
]

# Supported commands
SUPPORTED_COMMANDS = ["start", "stop", "diagnostic"]

# Configuration from environment variables
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# Example: If you have device IP or port, you can use them here
DEVICE_IP = os.getenv("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.getenv("DEVICE_PORT", "12345"))  # Not used in dummy, but for real device connection

class DeviceHTTPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode())
        elif self.path == "/data":
            self._set_headers(content_type="text/csv")
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=DUMMY_DATA[0].keys())
            writer.writeheader()
            for row in DUMMY_DATA:
                writer.writerow(row)
            self.wfile.write(output.getvalue().encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data)
                command = data.get("command")
                if command in SUPPORTED_COMMANDS:
                    # Here you would send the command to the actual device
                    response = {
                        "status": "success",
                        "command": command,
                        "message": f"Command '{command}' sent to device."
                    }
                    self._set_headers()
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": "Unsupported command"}).encode())
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()