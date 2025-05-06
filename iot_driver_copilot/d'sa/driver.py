import os
import threading
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

# Device Info (hardcoded as per provided info)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Helper function to get environment variables with defaults
def getenv(name, default=None, required=False):
    v = os.environ.get(name, default)
    if required and v is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

# Device configuration via environment variables
DEVICE_IP = getenv("DEVICE_IP", required=True)
DEVICE_PORT = int(getenv("DEVICE_PORT", 9000))      # Port for device protocol 'dsad'
SERVER_HOST = getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(getenv("SERVER_PORT", 8080))

# Simulated device connection for 'dsad' protocol (dummy XML for illustration)
def fetch_device_data():
    # Simulate fetching data from device (over TCP, etc.)
    # Replace this with actual protocol logic
    # For demonstration, we return static XML data
    xml_data = '''<data>
        <temperature>25.2</temperature>
        <humidity>58</humidity>
        <status>OK</status>
    </data>'''
    return xml_data

def send_device_command(cmd_xml):
    # Simulate sending a command to the device and getting a response
    # Replace this with actual protocol logic
    # For demonstration, echo back a success XML
    try:
        root = ET.fromstring(cmd_xml)
        resp = ET.Element("response")
        resp.text = "Command received"
        return ET.tostring(resp, encoding='utf-8', xml_declaration=True)
    except Exception as ex:
        resp = ET.Element("error")
        resp.text = f"Malformed XML: {str(ex)}"
        return ET.tostring(resp, encoding='utf-8', xml_declaration=True)

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            self.handle_get_data()
        elif parsed_path.path == "/info":
            self.handle_get_info()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            self.handle_post_cmd()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def handle_get_data(self):
        # Convert device protocol (dsad/XML) into HTTP response
        xml_data = fetch_device_data()
        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(xml_data.encode('utf-8'))

    def handle_post_cmd(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        # Expecting XML payload
        resp_xml = send_device_command(body)
        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(resp_xml)

    def handle_get_info(self):
        info_xml = ET.Element("device_info")
        for k, v in DEVICE_INFO.items():
            sub = ET.SubElement(info_xml, k)
            sub.text = v
        xml_bytes = ET.tostring(info_xml, encoding='utf-8', xml_declaration=True)
        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.end_headers()
        self.wfile.write(xml_bytes)

    def log_message(self, format, *args):
        # Silence default logging
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()