import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socket
import xml.etree.ElementTree as ET

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Environment variable config
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", 9000))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", 8080))

class DeviceConnectionError(Exception):
    pass

def fetch_device_data():
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(b"<get_data/>\n")
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode()
    except Exception as e:
        raise DeviceConnectionError(f"Could not fetch device data: {e}")

def send_device_command(cmd_xml):
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(cmd_xml.encode() + b"\n")
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode()
    except Exception as e:
        raise DeviceConnectionError(f"Could not send command: {e}")

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
            try:
                data = fetch_device_data()
                self._set_headers(200, "application/xml")
                self.wfile.write(data.encode())
            except DeviceConnectionError as e:
                self._set_headers(502, "text/plain")
                self.wfile.write(str(e).encode())
        elif self.path == "/info":
            info_xml = ET.Element("device_info")
            for k, v in DEVICE_INFO.items():
                child = ET.SubElement(info_xml, k)
                child.text = v
            self._set_headers(200, "application/xml")
            self.wfile.write(ET.tostring(info_xml))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                ET.fromstring(post_data)  # Validate XML
                resp = send_device_command(post_data.decode())
                self._set_headers(200, "application/xml")
                self.wfile.write(resp.encode())
            except ET.ParseError:
                self._set_headers(400, "text/plain")
                self.wfile.write(b"Invalid XML payload")
            except DeviceConnectionError as e:
                self._set_headers(502, "text/plain")
                self.wfile.write(str(e).encode())
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running at http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()