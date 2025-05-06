import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import urllib.parse

# Configuration from environment
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device static info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Dummy XML response for /data endpoint
def fetch_device_data():
    # Simulate fetching XML data from the device using the custom protocol.
    # In a real driver, this would involve parsing the "dsad" protocol.
    xml_data = f"""<?xml version="1.0" encoding="UTF-8"?>
<data>
    <point name="dsa" value="42"/>
</data>
"""
    return xml_data

# Dummy function to send command to device
def send_device_command(xml_command):
    # In a real driver, this would send the command using the "dsad" protocol.
    # Here, we simulate an XML response.
    response = f"""<?xml version="1.0" encoding="UTF-8"?>
<commandResponse status="success"/>
"""
    return response

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/data':
            # Proxy: Fetch XML data from device (simulate)
            xml_data = fetch_device_data()
            self._set_headers(200, "application/xml")
            self.wfile.write(xml_data.encode('utf-8'))
        elif parsed_path.path == '/info':
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not Found"}')

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            # Expect XML command in the body
            try:
                ET.fromstring(body)
                # Proxy: Send to device (simulate)
                xml_resp = send_device_command(body.decode('utf-8'))
                self._set_headers(200, "application/xml")
                self.wfile.write(xml_resp.encode('utf-8'))
            except ET.ParseError:
                self._set_headers(400, "application/json")
                self.wfile.write(b'{"error": "Invalid XML payload"}')
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not Found"}')

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Starting HTTP server at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run_server()