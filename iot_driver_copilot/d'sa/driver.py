import os
import threading
import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
from io import BytesIO

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Dummy device data for simulation (replace with actual device communication logic)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulated data points
DEVICE_DATA_POINTS = {
    "dsa": 42
}

# Simulated command execution
def perform_device_command(cmd_xml):
    # Parse XML and simulate a response
    try:
        root = ET.fromstring(cmd_xml)
        action = root.findtext('action') or "none"
        response = ET.Element('response')
        status = ET.SubElement(response, 'status')
        status.text = "success"
        performed = ET.SubElement(response, 'performed')
        performed.text = action
        return ET.tostring(response, encoding='utf-8')
    except ET.ParseError:
        response = ET.Element('response')
        status = ET.SubElement(response, 'status')
        status.text = "error"
        message = ET.SubElement(response, 'message')
        message.text = "Malformed XML"
        return ET.tostring(response, encoding='utf-8')

# Simulate device data fetch (replace with real device XML fetch)
def fetch_device_data():
    root = ET.Element('data')
    for key, value in DEVICE_DATA_POINTS.items():
        el = ET.SubElement(root, key)
        el.text = str(value)
    return ET.tostring(root, encoding='utf-8')

class DeviceHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/xml', status=200):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
            self._set_headers()
            data = fetch_device_data()
            self.wfile.write(data)
        elif self.path == "/info":
            self._set_headers('application/json')
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        else:
            self._set_headers('text/plain', 404)
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Accept only XML payload
            response = perform_device_command(post_data.decode('utf-8'))
            self._set_headers()
            self.wfile.write(response)
        else:
            self._set_headers('text/plain', 404)
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        return  # Suppress default logging

def run_server():
    with socketserver.ThreadingTCPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()