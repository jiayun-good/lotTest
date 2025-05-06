import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulate device XML data
def fetch_device_data():
    # In real case, connect to device via its protocol
    xml_data = f"""
    <Device>
        <Status>Online</Status>
        <DataPoints>
            <Point name="dsa" value="123"/>
        </DataPoints>
    </Device>
    """
    return xml_data.strip()

# Simulate sending a command to the device and getting a result
def send_device_command(xml_cmd):
    # In real case, send xml_cmd to device and get response
    result = f"""
    <CommandResponse>
        <Result>Success</Result>
        <Echo>{xml_cmd}</Echo>
    </CommandResponse>
    """
    return result.strip()

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/xml'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/data":
            self._set_headers(200, 'application/xml')
            xml_output = fetch_device_data()
            self.wfile.write(xml_output.encode('utf-8'))
        elif url.path == "/info":
            self._set_headers(200, 'application/json')
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b"Not Found")

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._set_headers(400, 'text/plain')
                self.wfile.write(b"No command data provided")
                return
            post_data = self.rfile.read(content_length)
            try:
                # Assume XML commands are sent
                ET.fromstring(post_data)  # Validate XML
            except ET.ParseError:
                self._set_headers(400, 'text/plain')
                self.wfile.write(b"Invalid XML payload")
                return
            response_xml = send_device_command(post_data.decode('utf-8'))
            self._set_headers(200, 'application/xml')
            self.wfile.write(response_xml.encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Override to prevent default stdout logging
        pass

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()