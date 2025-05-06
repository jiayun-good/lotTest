import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

# ----------------- Configuration from Environment Variables -----------------
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
DEVICE_USERNAME = os.environ.get("DEVICE_USERNAME", "admin")
DEVICE_PASSWORD = os.environ.get("DEVICE_PASSWORD", "admin")

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# ----------------- Device Info -----------------
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# ----------------- Mock Device Communication (over 'dsad' protocol) -----------------
# Simulate XML data from device
def get_device_data_points():
    # Example XML response
    root = ET.Element('DataPoints')
    dp = ET.SubElement(root, 'Point', name="temperature")
    dp.text = "23.5"
    dp2 = ET.SubElement(root, 'Point', name="humidity")
    dp2.text = "54"
    return ET.tostring(root, encoding="utf-8", method="xml")

def send_device_command(xml_payload):
    # Simulate sending XML command to device and getting response
    root = ET.Element('CommandResponse')
    status = ET.SubElement(root, 'Status')
    status.text = "Success"
    return ET.tostring(root, encoding="utf-8", method="xml")

# ----------------- HTTP Handler -----------------
class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            # Fetch current data points (XML from device, serve as JSON)
            xml_data = get_device_data_points()
            # Convert XML to dict for JSON response
            root = ET.fromstring(xml_data)
            data = {}
            for p in root.findall('Point'):
                data[p.attrib['name']] = p.text
            import json
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({"data_points": data}).encode("utf-8"))
        elif parsed_path.path == "/info":
            import json
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(DEVICE_INFO).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b"Not found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expect XML payload, send to device, get XML response
            device_resp = send_device_command(post_data)
            # Convert XML response to JSON
            root = ET.fromstring(device_resp)
            status = root.find('Status').text if root.find('Status') is not None else "Unknown"
            import json
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps({"result": status}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        # Suppress default logging; comment out to enable
        return

# ----------------- HTTP Server Boot -----------------
def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Starting HTTP server at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()