import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Mock device communication functions
def fetch_device_data(ip, port):
    # Simulate fetching XML data from device
    # In a real driver, this would open a socket or HTTP connection to the device.
    return """<?xml version="1.0"?><data><point1>123</point1><point2>456</point2></data>"""

def send_device_command(ip, port, command_xml):
    # Simulate sending a command to the device, and getting a response
    # In a real driver, this would send XML over TCP/HTTP to the device.
    return """<?xml version="1.0"?><response><status>success</status></response>"""

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/info":
            self._set_headers(200, "application/json")
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"]
            }
            import json
            self.wfile.write(json.dumps(info).encode())
            return
        elif parsed.path == "/data":
            self._set_headers(200, "application/xml")
            xml_data = fetch_device_data(
                os.environ.get("DEVICE_IP"),
                int(os.environ.get("DEVICE_PORT", "80"))
            )
            self.wfile.write(xml_data.encode())
            return
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            command_xml = post_data.decode()
            resp = send_device_command(
                os.environ.get("DEVICE_IP"),
                int(os.environ.get("DEVICE_PORT", "80")),
                command_xml
            )
            self._set_headers(200, "application/xml")
            self.wfile.write(resp.encode())
            return
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

def run():
    server_host = os.environ.get("SERVER_HOST", "0.0.0.0")
    server_port = int(os.environ.get("SERVER_PORT", "8080"))
    httpd = HTTPServer((server_host, server_port), DeviceHTTPRequestHandler)
    print(f"Starting HTTP server on {server_host}:{server_port}")
    httpd.serve_forever()

if __name__ == "__main__":
    # Ensure required environment variables are set
    for var in ["DEVICE_IP"]:
        if not os.environ.get(var):
            print(f"Environment variable {var} is required.")
            sys.exit(1)
    run()