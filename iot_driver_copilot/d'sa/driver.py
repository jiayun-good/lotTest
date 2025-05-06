import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import socket
import xml.etree.ElementTree as ET

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def fetch_device_data():
    """Connects to the device and retrieves XML data."""
    data = b""
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            # Example protocol: send a request for data points
            s.sendall(b'<get datapoints="all"/>')
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
    except Exception as e:
        data = f"<error>{str(e)}</error>".encode()
    return data

def send_device_command(command_xml):
    """Sends a command XML to the device and returns its response."""
    resp = b""
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(command_xml)
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                resp += chunk
    except Exception as e:
        resp = f"<error>{str(e)}</error>".encode()
    return resp

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        elif parsed_path.path == '/data':
            self._set_headers(200, "application/xml")
            data = fetch_device_data()
            self.wfile.write(data)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Assume the command is sent in XML format
            try:
                ET.fromstring(post_data)  # Validate XML
            except Exception:
                self._set_headers(400, "text/plain")
                self.wfile.write(b"Invalid XML")
                return
            response = send_device_command(post_data)
            self._set_headers(200, "application/xml")
            self.wfile.write(response)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return  # Silence logging

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Starting HTTP server at {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        pass