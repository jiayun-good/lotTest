import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Configuration from environment variables
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

def fetch_device_data():
    """
    Connects to the device via TCP socket, receives XML data, and returns it as string.
    """
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((DEVICE_IP, DEVICE_PORT))
            # Protocol-specific handshake or request may be required.
            # For this example, assume we send nothing and receive data directly.
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"</data>" in data or b"</status>" in data:
                    break
            return data.decode(errors="ignore")
    except Exception as e:
        return None

def send_device_command(cmd_xml):
    """
    Sends an XML command to the device and returns its response as string.
    """
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((DEVICE_IP, DEVICE_PORT))
            s.sendall(cmd_xml.encode())
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"</response>" in data:
                    break
            return data.decode(errors="ignore")
    except Exception as e:
        return None

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(str(DEVICE_INFO).replace("'", '"').encode())
        elif self.path == "/data":
            xml_data = fetch_device_data()
            if xml_data is None:
                self._set_headers(500)
                self.wfile.write(b'{"error": "Failed to retrieve data from device"}')
                return
            # Convert XML to JSON-like dict for browser consumption
            try:
                root = ET.fromstring(xml_data)
                data_dict = {root.tag: {child.tag: child.text for child in root}}
                import json
                self._set_headers()
                self.wfile.write(json.dumps(data_dict).encode())
            except Exception:
                self._set_headers(200, "application/xml")
                self.wfile.write(xml_data.encode())
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Expecting XML payload
                cmd_xml = post_data.decode()
                response = send_device_command(cmd_xml)
                if response is None:
                    self._set_headers(500)
                    self.wfile.write(b'{"error": "Failed to send command to device"}')
                    return
                self._set_headers(200, "application/xml")
                self.wfile.write(response.encode())
            except Exception:
                self._set_headers(400)
                self.wfile.write(b'{"error": "Invalid command payload"}')
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def log_message(self, format, *args):
        # Optional: silence default logging or output to a file
        pass

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), SimpleHTTPRequestHandler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()