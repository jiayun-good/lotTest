import os
import sys
import socket
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET
import urllib.parse

# ENVIRONMENT VARIABLES
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# DEVICE INFO (hardcoded based on provided info)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def fetch_device_data():
    # Simulate connection to device and retrieving XML data
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(b"<get_data/>")
            data = s.recv(4096)
            return data.decode('utf-8')
    except Exception as e:
        return "<error>{}</error>".format(str(e))

def send_device_command(xml_command):
    # Simulate sending XML command and getting XML response
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(xml_command.encode('utf-8'))
            data = s.recv(4096)
            return data.decode('utf-8')
    except Exception as e:
        return "<error>{}</error>".format(str(e))

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/xml"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers("application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        elif self.path == '/data':
            self._set_headers("application/xml")
            xml_data = fetch_device_data()
            self.wfile.write(bytes(xml_data, 'utf-8'))
        else:
            self.send_error(404, "Path not found")

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Assume XML command payload in POST body
            xml_command = post_data.decode('utf-8')
            response = send_device_command(xml_command)
            self._set_headers("application/xml")
            self.wfile.write(bytes(response, 'utf-8'))
        else:
            self.send_error(404, "Path not found")

    def log_message(self, format, *args):
        return  # Silence default logging

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Starting HTTP server on {SERVER_HOST}:{SERVER_PORT} (Device at {DEVICE_IP}:{DEVICE_PORT})")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()