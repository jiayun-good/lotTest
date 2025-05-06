import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET

# Environment Variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Dummy device XML response (simulate device for demonstration)
DUMMY_XML_DATA = """<?xml version="1.0" encoding="UTF-8"?>
<status>
    <data_point name="temperature" value="23.5"/>
    <data_point name="humidity" value="55"/>
</status>
"""

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

class DeviceConnectionError(Exception):
    pass

def fetch_device_data():
    # Simulate fetching XML from device over TCP/IP (dsad protocol stub)
    # Replace this with actual protocol implementation as needed.
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            sock.sendall(b"<getData/>")
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode("utf-8")
    except Exception:
        # For demonstration, fallback to dummy data
        return DUMMY_XML_DATA

def send_device_command(command_xml):
    # Simulate sending XML command and getting a response
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            sock.sendall(command_xml.encode("utf-8"))
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode("utf-8")
    except Exception:
        # Dummy response
        return """<response status="ok"/>"""

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", code=200):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers()
            self.wfile.write(bytes(str(DEVICE_INFO), 'utf-8'))
        elif self.path == '/data':
            xml_data = fetch_device_data()
            try:
                root = ET.fromstring(xml_data)
                data_points = []
                for dp in root.findall('data_point'):
                    data_points.append({
                        "name": dp.get("name"),
                        "value": dp.get("value")
                    })
                import json
                self._set_headers()
                self.wfile.write(json.dumps({"data_points": data_points}).encode("utf-8"))
            except Exception:
                self._set_headers('application/xml', 502)
                self.wfile.write(xml_data.encode("utf-8"))
        else:
            self._set_headers()
            self.wfile.write(b'{"error": "Not Found"}')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b''
            try:
                # Expecting command in JSON with { "command": ... }
                import json
                payload = json.loads(post_data.decode('utf-8'))
                command = payload.get("command", "")
                # Convert command to XML (stub)
                command_xml = f"<command>{command}</command>"
                response_xml = send_device_command(command_xml)
                try:
                    resp_root = ET.fromstring(response_xml)
                    result = {
                        "status": resp_root.get("status", "unknown")
                    }
                except Exception:
                    result = {"raw_response": response_xml}
                self._set_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
            except Exception:
                self._set_headers()
                self.wfile.write(b'{"error": "Invalid command payload"}')
        else:
            self._set_headers()
            self.wfile.write(b'{"error": "Not Found"}')

    def log_message(self, format, *args):
        return  # Silence default logging

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()