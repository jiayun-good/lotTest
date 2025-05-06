import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def get_env_or_default(var, default):
    return os.environ.get(var, default)

DEVICE_IP = get_env_or_default('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(get_env_or_default('DEVICE_PORT', '9000'))
SERVER_HOST = get_env_or_default('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(get_env_or_default('SERVER_PORT', '8080'))

# Simulated device XML endpoint
def fetch_device_xml_data():
    # In a real driver, connect to device and fetch XML.
    # Simulate device XML response:
    data = ET.Element("DeviceData")
    val = ET.SubElement(data, "DataPoint")
    val.set("name", "dsa")
    val.text = "42"
    return ET.tostring(data, encoding='utf-8', method='xml')

def send_device_command(xml_payload):
    # In a real driver, send XML command to device and get response.
    # Simulate a successful command response:
    resp = ET.Element("CommandResponse")
    status = ET.SubElement(resp, "Status")
    status.text = "Success"
    return ET.tostring(resp, encoding='utf-8', method='xml')

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self._set_headers()
            self.wfile.write(bytes(str({
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"]
            }), 'utf-8'))
        elif parsed_path.path == '/data':
            xml_data = fetch_device_xml_data()
            self._set_headers("application/xml")
            self.wfile.write(xml_data)
        else:
            self._set_headers("application/json", status=404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Assume XML payload to send to device
                xml_payload = ET.fromstring(post_data)
                resp_xml = send_device_command(ET.tostring(xml_payload))
                self._set_headers("application/xml")
                self.wfile.write(resp_xml)
            except Exception as e:
                self._set_headers("application/json", status=400)
                self.wfile.write(bytes('{"error": "Invalid XML payload"}', 'utf-8'))
        else:
            self._set_headers("application/json", status=404)
            self.wfile.write(b'{"error": "Not found"}')

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device driver HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()