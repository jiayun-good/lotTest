import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading

DEVICE_INFO = {
    "device_name": os.environ.get("DEVICE_NAME", "asdads"),
    "device_model": os.environ.get("DEVICE_MODEL", "ads"),
    "manufacturer": os.environ.get("DEVICE_MANUFACTURER", "asddas"),
    "device_type": os.environ.get("DEVICE_TYPE", "asd"),
    "connection_protocol": os.environ.get("DEVICE_PRIMARY_PROTOCOL", "asd"),
}

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulate device data and command interface
class DeviceSimulator:
    def __init__(self):
        self.data_output = {"value": 42, "status": "OK"}
        self.commands = []

    def get_data(self):
        return self.data_output

    def execute_command(self, cmd):
        self.commands.append(cmd)
        # Respond with simulated device response
        return {"result": "success", "executed": cmd}

device_sim = DeviceSimulator()

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps({
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"],
                "connection_protocol": DEVICE_INFO["connection_protocol"]
            }).encode())
        elif self.path == "/data":
            self._set_headers()
            self.wfile.write(json.dumps(device_sim.get_data()).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                cmd = json.loads(post_data.decode())
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            result = device_sim.execute_command(cmd)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()