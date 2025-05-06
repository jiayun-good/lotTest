import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json

# Read configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
DSA_PORT = int(os.environ.get("DSA_PORT", "9000"))  # Port to connect to dsa device

DEVICE_INFO = {
    "device_name": "asd",
    "device_model": "sda",
    "manufacturer": "sad",
    "device_type": "asd"
}

# Example real-time data points (simulate CSV data)
DATA_POINTS = [
    ["timestamp", "temperature", "humidity", "status"],
    ["2024-06-12T12:34:56Z", "23.1", "40", "OK"],
    ["2024-06-12T12:35:56Z", "23.2", "41", "OK"]
]

# Simulate device connection, real device logic/connection should be implemented here
def get_device_csv_data():
    # In a real implementation, connect to the DSA device (e.g., using socket), retrieve and parse CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    for row in DATA_POINTS:
        writer.writerow(row)
    return output.getvalue()

def send_device_command(command):
    # In a real implementation, connect to the DSA device and send the command, then get response
    # For demonstration, simply echo the command
    return {"result": "success", "command": command}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", status=200, extra_headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode())
        elif self.path == "/data":
            csv_data = get_device_csv_data()
            self._set_headers(content_type="text/csv")
            self.wfile.write(csv_data.encode())
        else:
            self._set_headers(status=404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode())
                command = payload.get("command")
                if not command:
                    raise ValueError("Missing command")
                result = send_device_command(command)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self._set_headers(status=400)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(status=404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Starting HTTP server on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()