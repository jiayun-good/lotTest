import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import threading

# ---------- Device Driver Mock/Placeholder Logic (since 'dsad' protocol is undefined) ----------

def fetch_device_data_points(device_ip, device_port):
    # Simulate fetching XML data from a device using a custom protocol (dsad)
    # In a real scenario, this would open a TCP socket to the device and request XML data.
    # Here, we return a static XML for illustration.
    xml = """
    <data>
        <temperature>24.5</temperature>
        <humidity>60</humidity>
        <status>ok</status>
    </data>
    """
    return xml.strip()

def send_device_command(device_ip, device_port, command_xml):
    # Simulate sending command XML to device and getting a response.
    # In a real scenario, this would open a TCP socket to the device and send XML.
    # Here, we mock a success response.
    response = """
    <response>
        <result>success</result>
    </response>
    """
    return response.strip()

# ---------- HTTP Server Implementation ----------

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), "utf-8"))
        elif path == "/data":
            xml_data = fetch_device_data_points(DEVICE_IP, DEVICE_PORT)
            self._set_headers(200, "application/xml")
            self.wfile.write(bytes(xml_data, "utf-8"))
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                command_xml = post_data.decode("utf-8")
                # Validate XML
                ET.fromstring(command_xml)
            except Exception as e:
                self._set_headers(400, "application/json")
                self.wfile.write(b'{"error": "Invalid XML payload"}')
                return

            response_xml = send_device_command(DEVICE_IP, DEVICE_PORT, command_xml)
            self._set_headers(200, "application/xml")
            self.wfile.write(bytes(response_xml, "utf-8"))
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not found"}')

    def log_message(self, format, *args):
        # Silence standard HTTP server logs
        return

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()