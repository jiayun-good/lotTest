import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import xml.etree.ElementTree as ET

DEVICE_NAME = os.environ.get("DEVICE_NAME", "d'sa")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "dsad'sa")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "dasdasdas")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "dsa")
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

class DeviceDriverHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(bytes(
                '{"device_name":"%s","device_model":"%s","manufacturer":"%s","device_type":"%s"}' %
                (DEVICE_NAME, DEVICE_MODEL, DEVICE_MANUFACTURER, DEVICE_TYPE), "utf-8"))
        elif self.path == "/data":
            try:
                xml_data = fetch_device_data()
                self._set_headers(content_type="application/xml")
                self.wfile.write(xml_data)
            except Exception as e:
                self._set_headers(502)
                self.wfile.write(bytes('<error>%s</error>' % str(e), "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                response_xml = send_device_command(post_data)
                self._set_headers(content_type="application/xml")
                self.wfile.write(response_xml)
            except Exception as e:
                self._set_headers(502)
                self.wfile.write(bytes('<error>%s</error>' % str(e), "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

def fetch_device_data():
    # Connects to the device and retrieves data in XML format.
    with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
        # The device-specific protocol: Here we assume sending 'GET_DATA' command retrieves data.
        s.sendall(b'GET_DATA\n')
        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        # Validate or parse XML
        try:
            ET.fromstring(data.decode("utf-8"))
        except Exception:
            raise RuntimeError("Invalid XML received from device")
        return data

def send_device_command(command_payload):
    # Sends a command to the device and returns the XML response.
    with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
        # The device-specific protocol: Here we pass on the payload directly.
        s.sendall(command_payload + b"\n")
        data = b""
        while True:
            chunk = s.recv(4096)
            if not chunk:
                break
            data += chunk
        # Validate or parse XML
        try:
            ET.fromstring(data.decode("utf-8"))
        except Exception:
            raise RuntimeError("Invalid XML received from device")
        return data

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceDriverHandler)
    print(f"HTTP Device Driver running at http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()