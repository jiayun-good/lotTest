import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

DEVICE_NAME = os.environ.get("DEVICE_NAME", "asdads")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "ads")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "asddas")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "asd")
PRIMARY_PROTOCOL = os.environ.get("PRIMARY_PROTOCOL", "asd")
DATA_POINTS = os.environ.get("DATA_POINTS", "asd")
COMMANDS = os.environ.get("COMMANDS", "dsa")
DATA_FORMAT = os.environ.get("DATA_FORMAT", "JSON")

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))

# Simulated device state for demonstration purposes
device_state = {
    "status": "idle",
    "metrics": {
        "asd": 0
    }
}

def fetch_device_data():
    # Simulate reading from the device's proprietary protocol (asd)
    # In a real implementation, you'd connect to DEVICE_IP:DEVICE_PORT,
    # speak the 'asd' protocol, and parse its response.
    return {
        "asd": device_state["metrics"]["asd"]
    }

def send_device_command(command):
    # Simulate sending command to the device and updating the device state
    # In a real implementation, you'd connect to DEVICE_IP:DEVICE_PORT and send the command.
    # Here, just update the device_state for demonstration.
    if "set" in command:
        device_state["metrics"]["asd"] = command.get("set", device_state["metrics"]["asd"])
        device_state["status"] = "set"
        return {"result": "success"}
    device_state["status"] = "unknown command"
    return {"result": "error", "reason": "Unknown command"}

class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", code=200):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            self._set_headers()
            data = fetch_device_data()
            self.wfile.write(json.dumps(data).encode())
        elif parsed_path.path == "/info":
            self._set_headers()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": DEVICE_MANUFACTURER,
                "device_type": DEVICE_TYPE,
                "primary_protocol": PRIMARY_PROTOCOL
            }
            self.wfile.write(json.dumps(info).encode())
        else:
            self._set_headers(code=404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                command = json.loads(body)
            except Exception:
                self._set_headers(code=400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            result = send_device_command(command)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self._set_headers(code=404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def log_message(self, format, *args):
        return  # Suppress default logging

def run_http_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, IoTDeviceHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_http_server()