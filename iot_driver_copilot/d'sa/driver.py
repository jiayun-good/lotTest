import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Device info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Mock device communication over "dsad" protocol (TCP, custom XML)
def get_device_data():
    # Simulate fetching XML data from device via TCP socket
    import socket
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=3) as s:
            request = "<get><datapoints /></get>"
            s.sendall(request.encode())
            data = b""
            while True:
                part = s.recv(4096)
                if not part:
                    break
                data += part
            return data.decode()
    except Exception as e:
        # Device offline or protocol error
        return f"<error>{str(e)}</error>"

def send_device_command(command_xml):
    import socket
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=3) as s:
            s.sendall(command_xml.encode())
            data = b""
            while True:
                part = s.recv(4096)
                if not part:
                    break
                data += part
            return data.decode()
    except Exception as e:
        return f"<error>{str(e)}</error>"

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode())
        elif self.path == "/data":
            data = get_device_data()
            self._set_headers()
            self.wfile.write(data.encode())
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Assume command payload is XML
                ET.fromstring(post_data.decode())
                device_response = send_device_command(post_data.decode())
                self._set_headers()
                self.wfile.write(device_response.encode())
            except ET.ParseError:
                self._set_headers(400, "application/xml")
                self.wfile.write(b"<error>Invalid XML payload</error>")
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Suppress default logging
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device driver HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()