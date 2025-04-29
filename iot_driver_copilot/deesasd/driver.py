import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import socket

# Device driver for device "deesasd", model "das" (manufacturer: sad)
# Environment Variables:
#   DEVICE_IP: IP address of the device
#   DEVICE_PORT: Port for device (asd protocol)
#   SERVER_HOST: Host address for this HTTP server (default: 0.0.0.0)
#   SERVER_PORT: Port for this HTTP server (default: 8080)

DEVICE_IP = os.environ.get('DEVICE_IP')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

if not DEVICE_IP:
    raise EnvironmentError("DEVICE_IP environment variable is required.")

# Simulated "asd" protocol: for demo, we assume device returns ASCII JSON lines on TCP

def get_device_data():
    # Connects to the device and reads one data point (JSON string)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((DEVICE_IP, DEVICE_PORT))
        s.sendall(b'GET_DATA\n')
        raw = b''
        while not raw.endswith(b'\n'):
            chunk = s.recv(4096)
            if not chunk:
                break
            raw += chunk
        try:
            return json.loads(raw.decode())
        except Exception:
            return {"error": "Invalid data from device", "raw": raw.decode(errors='replace')}

def send_device_command(cmd_payload):
    # Sends a command to the device and returns response
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((DEVICE_IP, DEVICE_PORT))
        msg = 'CMD ' + json.dumps(cmd_payload) + '\n'
        s.sendall(msg.encode())
        raw = b''
        while not raw.endswith(b'\n'):
            chunk = s.recv(4096)
            if not chunk:
                break
            raw += chunk
        try:
            return json.loads(raw.decode())
        except Exception:
            return {"error": "Invalid response from device", "raw": raw.decode(errors='replace')}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            data = get_device_data()
            self._set_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data)
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
                return
            resp = send_device_command(payload)
            self._set_headers()
            self.wfile.write(json.dumps(resp).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode())

    def log_message(self, format, *args):
        # Suppress default HTTP server logging
        return

def run(server_class=HTTPServer, handler_class=DeviceHTTPRequestHandler):
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Device driver HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run()