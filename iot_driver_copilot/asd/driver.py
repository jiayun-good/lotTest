import os
import csv
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Read environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "12345"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8000"))

# Dummy device "dsa" protocol adapter - you must replace these with actual protocol handling logic if available
class DSADriver:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.lock = threading.Lock()
        # Example state
        self.last_command = None

    def get_info(self):
        return {
            "device_name": "asd",
            "device_model": "sda",
            "manufacturer": "sad",
            "device_type": "asd"
        }

    def get_data(self):
        # Simulate CSV data as a list of dicts
        data_points = [
            {"timestamp": "2024-06-01T12:00:00Z", "value1": 123, "value2": 456},
            {"timestamp": "2024-06-01T12:00:01Z", "value1": 124, "value2": 457},
        ]
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data_points[0].keys())
        writer.writeheader()
        writer.writerows(data_points)
        return output.getvalue()

    def post_command(self, cmd):
        with self.lock:
            self.last_command = cmd
            # Simulate command execution
            return {"status": "ok", "received_command": cmd}

device = DSADriver(DEVICE_IP, DEVICE_PORT)

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            info = device.get_info()
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif self.path == "/data":
            data_csv = device.get_data()
            self._set_headers(content_type="text/csv")
            self.wfile.write(data_csv.encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                if self.headers.get("Content-Type", "").startswith("application/json"):
                    cmd = json.loads(post_data.decode("utf-8"))
                else:
                    cmd = {"raw": post_data.decode("utf-8")}
            except Exception:
                self.send_error(400, "Invalid JSON")
                return
            result = device.post_command(cmd)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self.send_error(404, "Not Found")

def run(server_class=HTTPServer, handler_class=RequestHandler):
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()