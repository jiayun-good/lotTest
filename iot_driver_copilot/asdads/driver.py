import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DEVICE_NAME = os.environ.get('DEVICE_NAME', 'asdads')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'ads')
MANUFACTURER = os.environ.get('MANUFACTURER', 'asddas')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'asd')
PRIMARY_PROTOCOL = os.environ.get('PRIMARY_PROTOCOL', 'asd')

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))

SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

class DeviceDriverHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers_json(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self._set_headers_json()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": MANUFACTURER,
                "device_type": DEVICE_TYPE,
                "primary_protocol": PRIMARY_PROTOCOL
            }
            self.wfile.write(json.dumps(info).encode())
        elif parsed_path.path == '/data':
            self._set_headers_json()
            data = self.fetch_device_data()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode())
            except Exception:
                self.send_error(400, "Invalid JSON")
                return
            result = self.send_device_command(payload)
            self._set_headers_json()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404, "Not Found")

    def fetch_device_data(self):
        # Simulate fetching data from device over TCP (raw protocol "asd"), converting to JSON
        try:
            import socket
            with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=3) as s:
                s.sendall(b'GET_DATA\n')
                raw = b''
                while True:
                    part = s.recv(4096)
                    if not part:
                        break
                    raw += part
            try:
                # Try to parse as JSON
                return json.loads(raw.decode())
            except Exception:
                # Fallback: wrap raw data
                return {"raw_data": raw.decode(errors='ignore')}
        except Exception as e:
            return {"error": str(e)}

    def send_device_command(self, cmd):
        # Simulate sending a command to the device over TCP (raw protocol "asd")
        try:
            import socket
            with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=3) as s:
                s.sendall(json.dumps(cmd).encode() + b'\n')
                response = b''
                while True:
                    part = s.recv(4096)
                    if not part:
                        break
                    response += part
            try:
                return {"result": json.loads(response.decode())}
            except Exception:
                return {"result": response.decode(errors='ignore')}
        except Exception as e:
            return {"error": str(e)}

    def log_message(self, format, *args):
        # Suppress default logging
        return

def run():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceDriverHTTPRequestHandler)
    print(f"Device driver HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run()
