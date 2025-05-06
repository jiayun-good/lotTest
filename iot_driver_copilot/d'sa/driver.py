import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8000'))

# Device Info Constants
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulate device XML data points
def fetch_device_data():
    # Here you would connect via 'dsad' protocol to actual device
    # For demonstration, simulate with example XML
    # <datapoints><point name='temperature'>22</point></datapoints>
    xml_data = "<datapoints><point name='dsa'>example_value</point></datapoints>"
    return xml_data

# Simulate sending a command to the device and getting an XML response
def send_device_command(command_xml):
    # Here you would send command_xml via 'dsad' protocol to the device
    # For demonstration, simulate success response
    response = "<response><status>success</status></response>"
    return response

class IoTHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", code=200):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/info':
            self._set_headers("application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        elif self.path == '/data':
            xml_data = fetch_device_data()
            self._set_headers("application/xml")
            self.wfile.write(bytes(xml_data, 'utf-8'))
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', '0'))
            post_data = self.rfile.read(content_length)
            try:
                command_xml = post_data.decode('utf-8')
                # Very basic XML validation
                ET.fromstring(command_xml)
                device_response = send_device_command(command_xml)
                self._set_headers("application/xml")
                self.wfile.write(bytes(device_response, "utf-8"))
            except Exception as e:
                self.send_error(400, "Invalid XML or Command")
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        return  # Suppress default logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTHTTPRequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()