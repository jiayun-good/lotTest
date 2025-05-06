import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

# Configuration via environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Dummy Device Info (replace with actual device communication logic)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulated Data Point (replace with actual data retrieval from device)
def fetch_device_data():
    # Simulate an XML response from the device
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <data>
        <data_points>dsa</data_points>
        <status>OK</status>
    </data>"""
    return xml_response

# Simulated Command Execution (replace with actual command logic)
def send_device_command(xml_payload):
    # Simulate device handling the command
    try:
        root = ET.fromstring(xml_payload)
        # Example: just echo back the command
        command = root.find('command').text if root.find('command') is not None else 'unknown'
        response_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
        <command_response>
            <command>{command}</command>
            <result>success</result>
        </command_response>"""
        return response_xml
    except ET.ParseError:
        return """<?xml version="1.0" encoding="UTF-8"?><error>Malformed XML</error>"""

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "dsaDeviceDriver/1.0"

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"]
            }
            self.wfile.write(bytes(str(info).replace("'", '"'), 'utf-8'))
        elif parsed_path.path == '/data':
            # Connect to device and fetch XML data, convert to HTTP
            xml_data = fetch_device_data()
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"Not found"}')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            xml_payload = post_data.decode('utf-8')
            # Send command to device and proxy the XML response
            response_xml = send_device_command(xml_payload)
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(response_xml.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"Not found"}')

    def log_message(self, format, *args):
        # Suppress default console logging; remove this method to enable logging
        return

def run_server():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()