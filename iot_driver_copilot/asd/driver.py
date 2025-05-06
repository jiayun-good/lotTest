import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import json

# Configuration via environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Device Info
DEVICE_INFO = {
    "device_name": "asd",
    "device_model": "sda",
    "manufacturer": "sad",
    "device_type": "asd"
}

class DSADeviceClient:
    """
    Example client for the dsa protocol.
    This mocks a TCP socket communication for the dsa protocol.
    """

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_data(self):
        # Connect to the device and retrieve CSV data
        try:
            import socket
            with socket.create_connection((self.ip, self.port), timeout=5) as s:
                s.sendall(b"GET_DATA\n")
                buffer = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk
                text = buffer.decode("utf-8")
                return text.strip()
        except Exception as e:
            return None

    def send_command(self, command):
        # Connect and send a command, expecting a reply
        try:
            import socket
            with socket.create_connection((self.ip, self.port), timeout=5) as s:
                s.sendall(command.encode("utf-8") + b"\n")
                buffer = b""
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk
                text = buffer.decode("utf-8")
                return text.strip()
        except Exception as e:
            return None

device_client = DSADeviceClient(DEVICE_IP, DEVICE_PORT)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode("utf-8"))
        elif self.path == "/data":
            csv_data = device_client.get_data()
            if csv_data is None:
                self._set_headers(502, "application/json")
                self.wfile.write(json.dumps({"error": "Failed to retrieve data from device"}).encode("utf-8"))
                return
            self._set_headers(200, "text/csv")
            # If the data is already CSV, stream as is
            self.wfile.write(csv_data.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body)
                command = payload.get("command")
                if not command:
                    raise ValueError("Missing 'command' in payload")
                response = device_client.send_command(command)
                if response is None:
                    self._set_headers(502)
                    self.wfile.write(json.dumps({"error": "Failed to send command to device"}).encode("utf-8"))
                else:
                    self._set_headers(200)
                    self.wfile.write(json.dumps({"result": response}).encode("utf-8"))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        return  # Silence the default logging

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, Handler)
    print(f"DSA HTTP Driver running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()