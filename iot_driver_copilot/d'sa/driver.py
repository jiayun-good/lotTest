import os
import threading
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus
import xml.etree.ElementTree as ET

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device static info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulate a connection to device using a custom raw TCP/XML protocol (dsad)
def get_device_data():
    import socket
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(b"<GetData></GetData>")
            chunks = []
            while True:
                data = s.recv(4096)
                if not data:
                    break
                chunks.append(data)
            raw_xml = b''.join(chunks).decode('utf-8')
            # Validate/parse XML before returning
            ET.fromstring(raw_xml)  # Will raise if invalid
            return raw_xml
    except Exception as e:
        return f"<error>{str(e)}</error>"

def send_device_command(command_xml):
    import socket
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(command_xml.encode('utf-8'))
            chunks = []
            while True:
                data = s.recv(4096)
                if not data:
                    break
                chunks.append(data)
            raw_xml = b''.join(chunks).decode('utf-8')
            ET.fromstring(raw_xml)
            return raw_xml
    except Exception as e:
        return f"<error>{str(e)}</error>"

class IoTDeviceHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/xml", status=HTTPStatus.OK):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/info':
            self._set_headers("application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        elif parsed.path == '/data':
            self._set_headers()
            xml_data = get_device_data()
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self._set_headers("text/plain", HTTPStatus.NOT_FOUND)
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Validate input as XML
                ET.fromstring(post_data.decode('utf-8'))
                response_xml = send_device_command(post_data.decode('utf-8'))
                self._set_headers()
                self.wfile.write(response_xml.encode('utf-8'))
            except ET.ParseError:
                self._set_headers("text/plain", HTTPStatus.BAD_REQUEST)
                self.wfile.write(b"Invalid XML")
        else:
            self._set_headers("text/plain", HTTPStatus.NOT_FOUND)
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        pass  # Suppress default logging

def run_server():
    with socketserver.ThreadingTCPServer((SERVER_HOST, SERVER_PORT), IoTDeviceHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()