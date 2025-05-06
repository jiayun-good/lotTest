import os
import threading
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

# Device Info (static for /info endpoint)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Environment Variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))  # 'dsad' protocol port
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Protocol: 'dsad' - For this driver, we assume it is a TCP socket-based protocol using XML messages.

def fetch_data_from_device():
    """
    Connect to the device using the dsad protocol and fetch data points (XML formatted).
    """
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((DEVICE_IP, DEVICE_PORT))
            # Simulate a protocol message to request data points
            s.sendall(b"<get_data/>")
            data = s.recv(4096)
            return data.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

def send_command_to_device(cmd_xml: str):
    """
    Send command XML payload to the device and return its response.
    """
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((DEVICE_IP, DEVICE_PORT))
            s.sendall(cmd_xml.encode('utf-8'))
            resp = s.recv(4096)
            return resp.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

class DriverHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO), 'utf-8'))
        elif parsed.path == "/data":
            xml_data = fetch_data_from_device()
            self._set_headers(200, "application/xml")
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)
            # Assume command is sent as XML payload in body
            resp_xml = send_command_to_device(post_body.decode('utf-8'))
            self._set_headers(200, "application/xml")
            self.wfile.write(resp_xml.encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Silence the default HTTP server logging
        return

def run_server():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), DriverHTTPRequestHandler)
    print(f"HTTP server started on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()