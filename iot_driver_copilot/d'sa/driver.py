```python
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import socket

# Device info (hardcoded as per requirements)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Helper: get env with default and required flag
def get_env(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and val is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return val

# Configuration from environment variables
DEVICE_IP = get_env("DEVICE_IP", required=True)
DEVICE_PORT = int(get_env("DEVICE_PORT", "9000"))
DEVICE_TIMEOUT = float(get_env("DEVICE_TIMEOUT", "3.0"))
SERVER_HOST = get_env("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(get_env("SERVER_PORT", "8080"))


def fetch_data_from_device():
    """
    Connects to the device using the raw 'dsad' protocol (TCP socket),
    retrieves a single XML data point and returns as bytes.
    """
    with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=DEVICE_TIMEOUT) as sock:
        # Protocol for requesting data: send 'GET_DATA\n'
        sock.sendall(b'GET_DATA\n')
        # Read until EOF or socket closes (simulate device sends one XML response)
        data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        return data

def send_command_to_device(command_xml: bytes):
    """
    Sends the XML command payload to the device and returns the response.
    """
    with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=DEVICE_TIMEOUT) as sock:
        # Protocol for sending command: send 'CMD\n' + XML + '\nEND\n'
        sock.sendall(b'CMD\n')
        sock.sendall(command_xml)
        sock.sendall(b'\nEND\n')
        # Read response (XML)
        data = b''
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
        return data

class IoTDeviceHandler(BaseHTTPRequestHandler):
    server_version = "DsadHTTPDriver/1.0"
    def _set_headers(self, code=200, content_type='application/xml'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/info":
            self._set_headers(200, 'application/json')
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode())
        elif path == "/data":
            try:
                xml_data = fetch_data_from_device()
                self._set_headers(200, 'application/xml')
                self.wfile.write(xml_data)
            except Exception as e:
                self._set_headers(502, 'text/plain')
                self.wfile.write(f"Error fetching data: {e}".encode())
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b"Not Found")

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._set_headers(400, 'text/plain')
                self.wfile.write(b"Missing command payload")
                return
            command_xml = self.rfile.read(content_length)
            try:
                response_xml = send_command_to_device(command_xml)
                self._set_headers(200, 'application/xml')
                self.wfile.write(response_xml)
            except Exception as e:
                self._set_headers(502, 'text/plain')
                self.wfile.write(f"Error sending command: {e}".encode())
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Quiet by default, or you can print to stderr if needed
        pass

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, IoTDeviceHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
```
