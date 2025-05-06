```python
import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Read configuration from environment variables
DEVICE_HOST = os.environ.get('DEVICE_HOST', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device Info (static as per provided info)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Protocol: dsad (assume TCP socket, XML, custom protocol)
def fetch_device_data():
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(4)
            sock.connect((DEVICE_HOST, DEVICE_PORT))
            # Example: Request data as per hypothetical protocol
            # For this demo, let's say sending "GETDATA\n" gets a single XML response
            sock.sendall(b'GETDATA\n')
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

def send_device_command(command_xml):
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(4)
            sock.connect((DEVICE_HOST, DEVICE_PORT))
            # The device expects command as XML string ending with newline
            sock.sendall(command_xml.encode('utf-8') + b'\n')
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            return response.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), "utf-8"))
        elif self.path == '/data':
            xml_data = fetch_device_data()
            self._set_headers(200, "application/xml")
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Expecting command in XML format
                ET.fromstring(post_data.decode('utf-8'))  # Validate XML
                xml_response = send_device_command(post_data.decode('utf-8'))
                self._set_headers(200, "application/xml")
                self.wfile.write(xml_response.encode('utf-8'))
            except ET.ParseError:
                self._set_headers(400, "application/xml")
                self.wfile.write(b"<error>Invalid XML</error>")
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return  # Suppress console logging

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
```
