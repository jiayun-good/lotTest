import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

# Device configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", 9000))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8080))

# Device information
DEVICE_INFO = {
    "device_name": "asdads",
    "device_model": "ads",
    "manufacturer": "asddas",
    "device_type": "asd",
    "primary_protocol": "asd"
}

# Shared state for demonstration (simulate device)
device_state = {
    "value": 42  # Example data point
}

def read_device_data():
    # Simulate reading from device with proprietary 'asd' protocol over TCP
    # In a real implementation, replace with protocol-specific communication.
    # This function would connect to DEVICE_IP:DEVICE_PORT, send a request, and parse the response.
    return {"data_points": device_state["value"]}

def send_device_command(cmd):
    # Simulate sending a command to the device over the asd protocol
    # In a real implementation, send 'cmd' appropriately to the device.
    # Here, we update the state for demonstration.
    if isinstance(cmd, dict) and "set_value" in cmd:
        device_state["value"] = cmd["set_value"]
        return {"status": "success", "new_value": device_state["value"]}
    return {"status": "unknown_command"}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps({
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "connection_protocol": DEVICE_INFO["primary_protocol"]
            }).encode())
        elif parsed_path.path == "/data":
            self._set_headers()
            data = read_device_data()
            self.wfile.write(json.dumps(data).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                command = json.loads(body)
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            result = send_device_command(command)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run_server()