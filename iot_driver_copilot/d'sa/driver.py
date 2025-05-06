import os
import threading
import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
from io import BytesIO

# Configuration from environment variables
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

# Simulate device XML response for /data
def fetch_device_data():
    # In a real driver, connect via the actual protocol to the device and retrieve XML data.
    # Here, simulate device response for demonstration.
    device_data = ET.Element("DeviceData")
    datapoints = ET.SubElement(device_data, "DataPoints")
    datapoints.text = "dsa"  # Simulated data points value
    return ET.tostring(device_data, encoding='utf-8', method='xml')

# Simulate sending a command to the device and getting XML response
def send_device_command(command_xml):
    # In a real driver, connect and send command as per device protocol, receive XML.
    # Here, simulate device response.
    result = ET.Element("CommandResult")
    status = ET.SubElement(result, "Status")
    status.text = "Success"
    return ET.tostring(result, encoding='utf-8', method='xml')

class IoTHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            self._set_headers(200, "application/xml")
            data = fetch_device_data()
            self.wfile.write(data)
        elif parsed_path.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(
                bytes(
                    '{'
                    f'"device_name": "{DEVICE_INFO["device_name"]}", '
                    f'"device_model": "{DEVICE_INFO["device_model"]}", '
                    f'"manufacturer": "{DEVICE_INFO["manufacturer"]}", '
                    f'"device_type": "{DEVICE_INFO["device_type"]}"'
                    '}', 'utf-8'
                )
            )
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Endpoint not found.")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Assume XML command in body
                command_xml = post_data
                # Optionally: validate/parse input XML here
                response_xml = send_device_command(command_xml)
                self._set_headers(200, "application/xml")
                self.wfile.write(response_xml)
            except Exception as e:
                self._set_headers(400, "text/plain")
                self.wfile.write(b"Invalid command or error processing command.")
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Endpoint not found.")

    def log_message(self, format, *args):
        # Override to suppress default console logging, comment out to enable logs
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()