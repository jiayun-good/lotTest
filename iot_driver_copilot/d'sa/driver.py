import os
import threading
import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import json

# Env configuration
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Mock device communication (replace with real protocol as needed)
def fetch_device_data():
    # Simulate an XML response from the device
    xml_data = """
    <DeviceData>
        <DataPoint name="temperature" value="22.5"/>
        <DataPoint name="humidity" value="48"/>
        <Status code="OK"/>
    </DeviceData>
    """
    return xml_data.strip()

def send_device_command(command_xml):
    # Simulate sending a command and device response
    # Here we just parse and echo back for demonstration
    try:
        root = ET.fromstring(command_xml)
        cmd_name = root.tag
        response = f"<Response status='success' command='{cmd_name}'/>"
    except Exception as e:
        response = f"<Response status='error' message='{str(e)}'/>"
    return response

# Device metadata
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            self.handle_get_data()
        elif parsed_path.path == "/info":
            self.handle_get_info()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            self.handle_post_cmd()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

    def handle_get_data(self):
        xml_data = fetch_device_data()
        # Optionally, convert XML to JSON for browser
        try:
            root = ET.fromstring(xml_data)
            datapoints = []
            for dp in root.findall("DataPoint"):
                datapoints.append({
                    "name": dp.attrib.get("name"),
                    "value": dp.attrib.get("value")
                })
            status = root.find("Status")
            status_code = status.attrib.get("code") if status is not None else None
            resp = {
                "datapoints": datapoints,
                "status": status_code
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        except Exception:
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(xml_data.encode("utf-8"))

    def handle_get_info(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(DEVICE_INFO).encode("utf-8"))

    def handle_post_cmd(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        # Expect XML command payload
        response_xml = send_device_command(post_data.decode("utf-8"))
        try:
            # Try to parse and return JSON
            root = ET.fromstring(response_xml)
            resp = {k: v for k, v in root.attrib.items()}
            resp["status"] = root.attrib.get("status", "unknown")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(resp).encode("utf-8"))
        except Exception:
            self.send_response(200)
            self.send_header("Content-Type", "application/xml")
            self.end_headers()
            self.wfile.write(response_xml.encode("utf-8"))

    def log_message(self, format, *args):
        return  # Silence the default logging

def run_server():
    with socketserver.ThreadingTCPServer((SERVER_HOST, SERVER_PORT), SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()