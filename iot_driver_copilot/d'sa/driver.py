import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Environment variable configuration
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))        # Port for raw protocol connection
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))        # HTTP server port

# Device static info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Utility: Connect to the device, get XML data, and parse
def get_device_data():
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((DEVICE_IP, DEVICE_PORT))
            s.sendall(b"<get_data/>\n")  # Example protocol message (may need to change for real device)
            raw = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                raw += chunk
                if b"</data>" in raw or b"</Data>" in raw:
                    break
        # Parse XML data
        root = ET.fromstring(raw.decode("utf-8", errors="ignore"))
        return ET.tostring(root, encoding="utf-8", method="xml")
    except Exception as e:
        return None

def send_device_command(xml_command):
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((DEVICE_IP, DEVICE_PORT))
            s.sendall(xml_command.encode("utf-8"))
            # Expecting an XML response
            raw = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                raw += chunk
                if b"</response>" in raw or b"</Response>" in raw:
                    break
        return raw.decode("utf-8", errors="ignore")
    except Exception as e:
        return None

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
            data = get_device_data()
            if data is None:
                self._set_headers(502, "application/json")
                self.wfile.write(b'{"error": "Failed to fetch device data"}')
            else:
                self._set_headers(200, "application/xml")
                self.wfile.write(data)
        elif self.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(str.encode(str(DEVICE_INFO).replace("'", '"')))
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not Found"}')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expecting XML payload
            try:
                ET.fromstring(post_data.decode("utf-8"))  # Validate XML
            except Exception:
                self._set_headers(400, "application/json")
                self.wfile.write(b'{"error": "Invalid XML command"}')
                return
            result = send_device_command(post_data.decode("utf-8"))
            if result is None:
                self._set_headers(502, "application/json")
                self.wfile.write(b'{"error": "Device command failed"}')
            else:
                self._set_headers(200, "application/xml")
                self.wfile.write(result.encode("utf-8"))
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not Found"}')


def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device HTTP Driver running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()