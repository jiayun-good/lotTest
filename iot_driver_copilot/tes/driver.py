import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import xml.etree.ElementTree as ET
import urllib.parse
from io import BytesIO

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

# Get configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

class DeviceProtocolClient:
    """
    Simulates a client for the device's custom 'ttt' protocol.
    In a real driver, this would handle low-level protocol details.
    """

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_info(self):
        # Simulate fetching info from the device using 'ttt' protocol
        return {
            "device_name": DEVICE_INFO["device_name"],
            "device_model": DEVICE_INFO["device_model"],
            "manufacturer": DEVICE_INFO["manufacturer"],
            "device_type": DEVICE_INFO["device_type"],
            "primary_protocol": DEVICE_INFO["primary_protocol"]
        }

    def run_test_command(self):
        # Simulate test command; in reality, would send a protocol command
        return {"result": "success", "message": "Test command executed successfully."}

    def get_data(self):
        # Simulate fetching XML data
        root = ET.Element("DeviceData")
        ET.SubElement(root, "DataPoint").text = DEVICE_INFO["data_points"]
        ET.SubElement(root, "Status").text = "OK"
        return ET.tostring(root, encoding='utf-8')

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DriverHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    client = DeviceProtocolClient(DEVICE_IP, DEVICE_PORT)

    def _set_response(self, code=200, headers=None, content_type="application/json", content_length=None):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        if content_length is not None:
            self.send_header('Content-Length', str(content_length))
        if headers:
            for k, v in headers.items():
                self.send_header(k, v)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/info':
            info = self.client.get_info()
            response = {
                "device_name": info["device_name"],
                "device_model": info["device_model"],
                "manufacturer": info["manufacturer"],
                "primary_protocol": info["primary_protocol"]
            }
            data = bytes(str(response), 'utf-8')
            self._set_response(content_type='application/json', content_length=len(data))
            self.wfile.write(data)
        elif parsed_path.path == '/data':
            xml_data = self.client.get_data()
            self._set_response(content_type='application/xml', content_length=len(xml_data))
            self.wfile.write(xml_data)
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == '/test':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                self.rfile.read(content_length)  # Read and discard body
            result = self.client.run_test_command()
            data = bytes(str(result), 'utf-8')
            self._set_response(content_type='application/json', content_length=len(data))
            self.wfile.write(data)
        else:
            self.send_error(404, "Not found")

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, DriverHTTPRequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()