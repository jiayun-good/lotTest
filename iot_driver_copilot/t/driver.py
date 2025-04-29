import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

# Device simulation for "ttt" protocol (since no real protocol is specified)
class TTTDevice:
    def __init__(self, ip, datapoints):
        self.ip = ip
        self.datapoints = datapoints
        self.latest_data = {dp: 0 for dp in datapoints}
        self.lock = threading.Lock()

    def read_data(self):
        # Simulate reading data from the device
        with self.lock:
            # For example, just increment each data point for demonstration
            for dp in self.latest_data:
                self.latest_data[dp] += 1
            return self.latest_data.copy()

    def send_command(self, cmd):
        # Simulate sending a command to the device
        with self.lock:
            # Dummy command execution
            return {"result": "success", "cmd": cmd}

# Environment configuration
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
DATA_POINTS = os.environ.get("DATA_POINTS", "sensor1,sensor2").split(",")

device = TTTDevice(DEVICE_IP, DATA_POINTS)

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            data = device.read_data()
            self._set_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
                return
            cmd = payload.get("cmd")
            if not cmd:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing 'cmd' in payload"}).encode("utf-8"))
                return
            result = device.send_command(cmd)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), RequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()