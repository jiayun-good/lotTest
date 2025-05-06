import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading
import socket
import xml.etree.ElementTree as ET

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def get_device_data():
    """
    Connect to the device using the proprietary protocol (simulated here via TCP socket),
    fetch XML data, and return it as bytes. If connection fails, return an error XML.
    """
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            # Simulate protocol: send request for data points
            s.sendall(b'GET_DATA\n')
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data
    except Exception as e:
        # Return error XML
        root = ET.Element('error')
        message = ET.SubElement(root, 'message')
        message.text = str(e)
        return ET.tostring(root, encoding='utf-8', method='xml')

def send_device_command(command_xml):
    """
    Connect to the device and send the given command (as XML).
    Returns device response (as bytes).
    """
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            # Simulate protocol: send command
            s.sendall(b'SEND_CMD\n')
            s.sendall(command_xml)
            s.sendall(b'\nEND_CMD\n')
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data
    except Exception as e:
        # Return error XML
        root = ET.Element('error')
        message = ET.SubElement(root, 'message')
        message.text = str(e)
        return ET.tostring(root, encoding='utf-8', method='xml')

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            # Return device info as JSON
            import json
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        elif parsed_path.path == '/data':
            # Proxy device data as XML, readable via browser/cli
            data = get_device_data()
            self._set_headers(200, "application/xml")
            self.wfile.write(data)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expect XML payload
            try:
                # Validate XML (parsing)
                ET.fromstring(post_data)
            except ET.ParseError:
                self._set_headers(400, "application/xml")
                root = ET.Element('error')
                message = ET.SubElement(root, 'message')
                message.text = 'Invalid XML payload'
                self.wfile.write(ET.tostring(root, encoding='utf-8', method='xml'))
                return
            # Proxy command to device, return device XML response
            response = send_device_command(post_data)
            self._set_headers(200, "application/xml")
            self.wfile.write(response)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Suppress default logging
        pass

class ThreadedHTTPServer(HTTPServer, threading.Thread):
    def __init__(self, server_address, RequestHandlerClass):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)
        threading.Thread.__init__(self)
        self.daemon = True

    def run(self):
        self.serve_forever()

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running on {SERVER_HOST}:{SERVER_PORT}")
    server.run()

if __name__ == '__main__':
    run_server()