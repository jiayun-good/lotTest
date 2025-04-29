import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

# Device info (would typically come from device or config)
DEVICE_INFO = {
    "device_name": "tes",
    "device_model": "tt",
    "manufacturer": "ttt",
    "device_type": "ttt",
    "primary_protocol": "ttt",
    "data_points": "tt",
    "commands": "ttt",
    "data_format": "XML"
}

# Environment variables for configuration
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulated device interaction (replace with real device logic)
def get_device_data():
    # Simulate XML data from device
    root = ET.Element("DeviceData")
    status = ET.SubElement(root, "Status")
    status.text = "OK"
    datapoint = ET.SubElement(root, "DataPoint")
    datapoint.text = "42"
    return ET.tostring(root, encoding='utf-8', method='xml')

def execute_device_test():
    # Simulate device test command
    root = ET.Element("TestResult")
    success = ET.SubElement(root, "Success")
    success.text = "true"
    message = ET.SubElement(root, "Message")
    message.text = "Device test passed"
    return ET.tostring(root, encoding='utf-8', method='xml')

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type='application/json', code=200):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers('application/json')
            response = {
                "device_info": {
                    "device_name": DEVICE_INFO["device_name"],
                    "device_model": DEVICE_INFO["device_model"],
                    "manufacturer": DEVICE_INFO["manufacturer"],
                    "device_type": DEVICE_INFO["device_type"],
                },
                "connection_info": {
                    "primary_protocol": DEVICE_INFO["primary_protocol"],
                    "device_ip": DEVICE_IP,
                    "device_port": DEVICE_PORT
                }
            }
            self.wfile.write(bytes(str(response), "utf-8"))
        elif self.path == '/data':
            self._set_headers('application/xml')
            # Retrieve and stream XML data from device
            xml_data = get_device_data()
            self.wfile.write(xml_data)
        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        if self.path == '/test':
            self._set_headers('application/xml')
            # Execute test command on device and return XML result
            xml_result = execute_device_test()
            self.wfile.write(xml_result)
        else:
            self.send_error(404, "Endpoint not found")

    def log_message(self, format, *args):
        return  # Suppress logging

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running at http://{SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()