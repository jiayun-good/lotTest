import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json

# Device configuration from environment variables
DEVICE_NAME = os.environ.get("DEVICE_NAME", "asd")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "sda")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "sad")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "asd")

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Mock device data and command interface for demonstration
class DSADevice:
    def __init__(self):
        self.status = "idle"
        self.data_points = [
            {"timestamp": "2024-06-01T10:00:00Z", "value": 12.5, "unit": "C"},
            {"timestamp": "2024-06-01T10:01:00Z", "value": 12.7, "unit": "C"},
            {"timestamp": "2024-06-01T10:02:00Z", "value": 12.6, "unit": "C"},
        ]
        self.cmd_log = []

    def get_info(self):
        return {
            "device_name": DEVICE_NAME,
            "device_model": DEVICE_MODEL,
            "manufacturer": DEVICE_MANUFACTURER,
            "device_type": DEVICE_TYPE,
            "status": self.status
        }

    def get_csv_data(self):
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["timestamp", "value", "unit"])
        writer.writeheader()
        for data in self.data_points:
            writer.writerow(data)
        return output.getvalue()

    def execute_command(self, cmd):
        # Simulated command execution
        self.cmd_log.append(cmd)
        if cmd.get("action") == "start":
            self.status = "running"
            return {"result": "started"}
        elif cmd.get("action") == "stop":
            self.status = "stopped"
            return {"result": "stopped"}
        elif cmd.get("action") == "diagnostic":
            return {"result": "ok", "diagnostic": "all systems nominal"}
        else:
            return {"result": "unknown command"}

device = DSADevice()

class DriverHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            info = device.get_info()
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif self.path == '/data':
            csv_data = device.get_csv_data()
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv')
            self.send_header('Content-Disposition', 'inline; filename="data.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                cmd = json.loads(body)
            except Exception:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid JSON')
                return
            result = device.execute_command(cmd)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Disable default logging to keep output clean
        return

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DriverHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()