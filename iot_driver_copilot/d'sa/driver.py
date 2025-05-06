import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import xml.etree.ElementTree as ET

# Load configurations from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Device static info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulate device data
def fetch_device_data():
    # Connect to device's raw protocol port (simulate XML data over TCP)
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            sock.sendall(b"<getData/>")
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
        # Parse to ensure it's XML (just as an example)
        root = ET.fromstring(data.decode('utf-8'))
        return data.decode('utf-8')
    except Exception as e:
        # Return a simple XML error
        return f"<error>{str(e)}</error>"

def send_device_command(command_xml):
    # Send command to device (simulate XML command over TCP)
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            sock.sendall(command_xml.encode('utf-8'))
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
        # Assume response is XML
        root = ET.fromstring(data.decode('utf-8'))
        return data.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), "utf-8"))
        elif self.path == "/data":
            xml_data = fetch_device_data()
            self._set_headers(200, "application/xml")
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Assume command is XML in body
                command_xml = post_data.decode('utf-8')
                # Validate XML
                ET.fromstring(command_xml)
                resp = send_device_command(command_xml)
                self._set_headers(200, "application/xml")
                self.wfile.write(resp.encode('utf-8'))
            except Exception as e:
                self._set_headers(400, "application/xml")
                self.wfile.write(f"<error>{str(e)}</error>".encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        return  # Suppress default logging to stdout

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()