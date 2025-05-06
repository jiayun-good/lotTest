import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET
import socket

# Environment Variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', 9000))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', 8080))

# Device Info (static as per provided info)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Helper to communicate with the device over "dsad" protocol (mocked as TCP socket sending/receiving XML)
class DsadDeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def fetch_data(self):
        # Request device status/data points
        xml_request = "<get><what>dsa</what></get>"
        response = self._send_and_receive(xml_request)
        return response

    def send_command(self, command_xml):
        # Send command as XML string
        response = self._send_and_receive(command_xml)
        return response

    def _send_and_receive(self, xml_message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((self.ip, self.port))
            s.sendall(xml_message.encode('utf-8'))
            received = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                received += chunk
            return received.decode('utf-8')

# HTTP Handler
class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    device_client = DsadDeviceClient(DEVICE_IP, DEVICE_PORT)

    def do_GET(self):
        if self.path == "/info":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        elif self.path == "/data":
            try:
                xml_data = self.device_client.fetch_data()
                # Optionally: validate/parse XML and return as pretty XML or JSON
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml')
                self.end_headers()
                self.wfile.write(xml_data.encode('utf-8'))
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes('{"error":"%s"}' % str(e), 'utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length).decode('utf-8')
            # Accept XML command in the body directly
            try:
                # Optionally validate XML here
                ET.fromstring(post_body)  # Will raise if invalid
                response_xml = self.device_client.send_command(post_body)
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml')
                self.end_headers()
                self.wfile.write(response_xml.encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(bytes('{"error":"%s"}' % str(e), 'utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), IoTDeviceHTTPRequestHandler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()