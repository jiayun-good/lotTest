import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
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

class DSADDeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.lock = threading.Lock()

    def fetch_data(self):
        # Connects to the device and fetches XML data
        with self.lock:
            try:
                with socket.create_connection((self.ip, self.port), timeout=5) as s:
                    s.sendall(b'<get_data/>\n')
                    data = b''
                    while True:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                        if b'</data>' in data or b'</root>' in data:
                            break
                    # Return the XML as string
                    return data.decode('utf-8', errors='replace')
            except Exception as e:
                return f'<error>{str(e)}</error>'

    def send_command(self, command_xml):
        # Sends a command XML to the device, returns response XML
        with self.lock:
            try:
                with socket.create_connection((self.ip, self.port), timeout=5) as s:
                    s.sendall(command_xml.encode('utf-8') + b'\n')
                    data = b''
                    while True:
                        chunk = s.recv(4096)
                        if not chunk:
                            break
                        data += chunk
                        if b'</response>' in data or b'</root>' in data:
                            break
                    return data.decode('utf-8', errors='replace')
            except Exception as e:
                return f'<error>{str(e)}</error>'

client = DSADDeviceClient(DEVICE_IP, DEVICE_PORT)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
            return

        elif self.path == '/data':
            xml_data = client.fetch_data()
            try:
                # Optionally pretty-print XML or translate to JSON if needed
                root = ET.fromstring(xml_data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml')
                self.end_headers()
                self.wfile.write(xml_data.encode('utf-8'))
            except Exception:
                self.send_response(502)
                self.send_header('Content-Type', 'application/xml')
                self.end_headers()
                self.wfile.write(xml_data.encode('utf-8'))
            return

        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_response(400)
                self.end_headers()
                return
            command_body = self.rfile.read(content_length).decode('utf-8')
            # The payload should be XML as per device data_format
            if not command_body.strip().startswith('<'):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Payload must be XML')
                return
            response_xml = client.send_command(command_body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(response_xml.encode('utf-8'))
            return
        else:
            self.send_response(404)
            self.end_headers()

def run():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), SimpleHTTPRequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    run()
