import os
import threading
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Env config
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "8899"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Dummy device info (normally fetched from the device)
DEVICE_INFO = {
    "device_name": "tes",
    "device_model": "tt",
    "manufacturer": "ttt",
    "device_type": "ttt",
    "primary_protocol": "ttt"
}

# Simulated device XML data (normally fetched from the device)
def get_device_xml_data():
    root = ET.Element("DeviceData")
    ET.SubElement(root, "Temperature").text = "23.5"
    ET.SubElement(root, "Humidity").text = "45"
    return ET.tostring(root, encoding="utf-8")

# Simulated test command (normally sent to the device)
def perform_test_command():
    root = ET.Element("TestResult")
    ET.SubElement(root, "Status").text = "Success"
    ET.SubElement(root, "Message").text = "Device connectivity and command test passed"
    return ET.tostring(root, encoding="utf-8")

class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", code=200):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/info":
            self._set_headers(content_type="application/json")
            response = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"],
                "primary_protocol": DEVICE_INFO["primary_protocol"]
            }
            self.wfile.write(bytes(str(response).replace("'", '"'), "utf-8"))
        elif parsed_path.path == "/data":
            # Simulate fetching XML data from the device
            xml_data = get_device_xml_data()
            self._set_headers(content_type="application/xml")
            self.wfile.write(xml_data)
        else:
            self._set_headers(code=404)
            self.wfile.write(b'{"error": "Endpoint not found"}')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b""
        if parsed_path.path == "/test":
            # Simulate sending a command to the device
            xml_result = perform_test_command()
            self._set_headers(content_type="application/xml")
            self.wfile.write(xml_result)
        else:
            self._set_headers(code=404)
            self.wfile.write(b'{"error": "Endpoint not found"}')

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, IoTDeviceHTTPRequestHandler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()