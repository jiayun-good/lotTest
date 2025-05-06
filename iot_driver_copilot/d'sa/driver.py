import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import socket
import xml.etree.ElementTree as ET

# Device Info (hardcoded per your JSON above)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Required env vars
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))  # dsad protocol port
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Dummy Protocol: dsad
# Simulate a device connection over TCP, speaking a simple line-based XML protocol

def get_device_data():
    # Connects to device and gets XML data (simulate protocol)
    with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
        s.sendall(b'GET_DATA\n')
        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
            if b"</data>" in data:
                break
        return data.decode('utf-8')

def send_device_command(command_xml):
    # Connects to device and sends XML command, returns XML response
    with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
        s.sendall(command_xml.encode('utf-8') + b"\n")
        response = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            response += chunk
            if b"</response>" in response:
                break
        return response.decode('utf-8')

class DSADHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/info":
            self._set_headers()
            self.wfile.write(bytes(str({
                "device_name": DEVICE_INFO['device_name'],
                "device_model": DEVICE_INFO['device_model'],
                "manufacturer": DEVICE_INFO['manufacturer'],
                "device_type": DEVICE_INFO['device_type']
            }), "utf-8"))
        elif parsed.path == "/data":
            try:
                xml_data = get_device_data()
                # Parse XML and convert to JSON-style dict
                root = ET.fromstring(xml_data)
                data_dict = {child.tag: child.text for child in root}
                self._set_headers()
                self.wfile.write(bytes(str(data_dict), "utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(bytes('{"error":"%s"}' % str(e), "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not Found"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Expect raw XML in POST body
                command_xml = post_data.decode('utf-8')
                response_xml = send_device_command(command_xml)
                # Parse XML and convert to JSON-style dict
                root = ET.fromstring(response_xml)
                resp_dict = {child.tag: child.text for child in root}
                self._set_headers()
                self.wfile.write(bytes(str(resp_dict), "utf-8"))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(bytes('{"error":"%s"}' % str(e), "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not Found"}')

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DSADHTTPRequestHandler)
    print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()