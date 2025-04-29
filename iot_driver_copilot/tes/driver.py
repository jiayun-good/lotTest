import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device Info
DEVICE_INFO = {
    "device_name": "tes",
    "device_model": "tt",
    "manufacturer": "ttt",
    "device_type": "ttt",
    "primary_protocol": "ttt"
}

# Simulated device XML data
def get_device_xml_data():
    root = ET.Element("DeviceData")
    status = ET.SubElement(root, "Status")
    status.text = "OK"
    value = ET.SubElement(root, "Value")
    value.text = "42"
    return ET.tostring(root, encoding="utf-8", method="xml")

# Simulated device command execution
def execute_test_command():
    root = ET.Element("TestResult")
    result = ET.SubElement(root, "Result")
    result.text = "PASS"
    return ET.tostring(root, encoding="utf-8", method="xml")

# Simulated device connection (stub for actual protocol)
def fetch_device_status_xml():
    # In a real driver, this function would connect to DEVICE_IP:DEVICE_PORT
    # and retrieve the XML data using the device's protocol.
    return get_device_xml_data()

def run_test_command_on_device():
    # In a real driver, this function would send a command to the device and parse the response.
    return execute_test_command()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceDriverHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", status_code=200, extra_headers=None):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"],
                "primary_protocol": DEVICE_INFO["primary_protocol"],
                "ip": DEVICE_IP,
                "port": DEVICE_PORT
            }
            self.wfile.write(bytes(str(info), "utf-8"))
        elif self.path == "/data":
            xml_data = fetch_device_status_xml()
            self._set_headers(content_type="application/xml")
            self.wfile.write(xml_data)
        else:
            self._set_headers(status_code=404)
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/test":
            # Read and discard any posted data, not used for this command.
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length:
                self.rfile.read(content_length)
            xml_result = run_test_command_on_device()
            self._set_headers(content_type="application/xml")
            self.wfile.write(xml_result)
        else:
            self._set_headers(status_code=404)
            self.wfile.write(b"Not Found")

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceDriverHandler)
    print(f"Starting HTTP server on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()