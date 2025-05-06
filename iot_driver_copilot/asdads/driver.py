import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading
import socket

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_INFO = {
    "device_name": "asdads",
    "device_model": "ads",
    "manufacturer": "asddas",
    "device_type": "asd",
    "primary_protocol": "asd"
}

class SimpleASDClient:
    # Simulate raw device 'asd' protocol: Connect, send command, fetch data
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_command(self, command_payload):
        # Simulate sending a command and receiving ack
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((self.ip, self.port))
            message = json.dumps(command_payload).encode('utf-8')
            s.sendall(message)
            resp = s.recv(1024)
            try:
                return json.loads(resp.decode("utf-8"))
            except Exception:
                return {"status": "error", "response": resp.decode("utf-8")}

    def fetch_data(self):
        # Simulate fetching current device data
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((self.ip, self.port))
            s.sendall(b"GET_DATA")
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            try:
                return json.loads(data.decode("utf-8"))
            except Exception:
                return {"status": "error", "data": data.decode("utf-8")}

class ASDHTTPHandler(BaseHTTPRequestHandler):
    client = SimpleASDClient(DEVICE_IP, DEVICE_PORT)

    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/info":
            self._set_headers()
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "primary_protocol": DEVICE_INFO["primary_protocol"],
            }
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif parsed_path.path == "/data":
            self._set_headers()
            data = self.client.fetch_data()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "No payload"}).encode("utf-8"))
                return
            post_data = self.rfile.read(content_length)
            try:
                command_payload = json.loads(post_data)
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode("utf-8"))
                return
            result = self.client.send_command(command_payload)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), ASDHTTPHandler)
    print(f"ASD HTTP Device Driver running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
