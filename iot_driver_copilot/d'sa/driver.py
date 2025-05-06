import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import socket

# Configuration from environment variables
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

DATA_FORMAT = "XML"

# -- Device Protocol Simulation/Transport Layer (dsad protocol over TCP socket) --

def fetch_device_data():
    """
    Connects to the device using the 'dsad' protocol (simulated as raw TCP).
    Receives an XML string with device data points.
    """
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(b"<get_data/>\n")
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode("utf-8").strip()
    except Exception as e:
        return None

def send_device_command(command_xml):
    """
    Sends a command (XML) to the device using the 'dsad' protocol (simulated as raw TCP).
    Returns the device's XML response.
    """
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(command_xml.encode("utf-8") + b"\n")
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode("utf-8").strip()
    except Exception as e:
        return None

# -- HTTP API Handler --

class DeviceHTTPHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            resp = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"],
            }
            self.wfile.write(bytes(str(resp).replace("'", '"'), "utf-8"))
        elif self.path == "/data":
            device_xml = fetch_device_data()
            if device_xml is None:
                self._set_headers(502, "text/plain")
                self.wfile.write(b"Failed to fetch data from device.")
                return
            # Optionally, validate/parse XML here
            self._set_headers(200, "application/xml")
            self.wfile.write(device_xml.encode("utf-8"))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found.")

    def do_POST(self):
        if self.path == "/cmd":
            length = int(self.headers.get('Content-Length', 0))
            if length == 0:
                self._set_headers(400, "text/plain")
                self.wfile.write(b"Missing command payload.")
                return
            post_data = self.rfile.read(length)
            try:
                # For XML, accept as raw string
                command_xml = post_data.decode("utf-8")
                # Optionally, validate XML structure
                ET.fromstring(command_xml)
            except Exception:
                self._set_headers(400, "text/plain")
                self.wfile.write(b"Invalid XML payload.")
                return

            device_response = send_device_command(command_xml)
            if device_response is None:
                self._set_headers(502, "text/plain")
                self.wfile.write(b"Failed to send command to device.")
                return
            self._set_headers(200, "application/xml")
            self.wfile.write(device_response.encode("utf-8"))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found.")

    def log_message(self, format, *args):
        # Override to suppress logging to stderr
        pass

# -- HTTP Server Startup --

def run_server():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPHandler)
    print(f"Device HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()