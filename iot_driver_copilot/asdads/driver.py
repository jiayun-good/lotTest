import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading
import socket

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

DEVICE_INFO = {
    "device_name": "asdads",
    "device_model": "ads",
    "manufacturer": "asddas",
    "device_type": "asd",
    "primary_protocol": "asd"
}

class DeviceConnection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.lock = threading.Lock()

    def fetch_data(self):
        # Simulated raw data fetch from device over TCP socket
        try:
            with self.lock:
                s = socket.create_connection((self.ip, self.port), timeout=3)
                s.sendall(b'GET_DATA\n')
                chunks = []
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    chunks.append(chunk)
                s.close()
                data = b''.join(chunks)
                # Assume device returns JSON bytes
                return json.loads(data.decode())
        except Exception as e:
            return {"error": str(e)}

    def send_command(self, cmd_payload):
        # Simulated command send over TCP socket
        try:
            with self.lock:
                s = socket.create_connection((self.ip, self.port), timeout=3)
                s.sendall(b'CMD:' + json.dumps(cmd_payload).encode() + b'\n')
                resp = s.recv(4096)
                s.close()
                return json.loads(resp.decode())
        except Exception as e:
            return {"error": str(e)}

    def stream_data(self):
        # Simulated streaming from device (yields lines or chunks)
        try:
            with self.lock:
                s = socket.create_connection((self.ip, self.port), timeout=3)
                s.sendall(b'STREAM\n')
                while True:
                    chunk = s.recv(4096)
                    if not chunk:
                        break
                    yield chunk
                s.close()
        except Exception:
            return

device_conn = DeviceConnection(DEVICE_IP, DEVICE_PORT)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/info':
            self._set_headers()
            info = {
                "device_name": DEVICE_INFO['device_name'],
                "device_model": DEVICE_INFO['device_model'],
                "manufacturer": DEVICE_INFO['manufacturer'],
                "primary_protocol": DEVICE_INFO['primary_protocol']
            }
            self.wfile.write(json.dumps(info).encode())
        elif parsed.path == '/data':
            self._set_headers()
            data = device_conn.fetch_data()
            self.wfile.write(json.dumps(data).encode())
        elif parsed.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'close')
            self.end_headers()
            for chunk in device_conn.stream_data():
                self.wfile.write(chunk)
                self.wfile.flush()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"Not found"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                cmd_payload = json.loads(body.decode())
            except Exception:
                self._set_headers(400)
                self.wfile.write(b'{"error":"Invalid JSON"}')
                return
            result = device_conn.send_command(cmd_payload)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"Not found"}')

def run_server():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), SimpleHTTPRequestHandler)
    print(f'Serving HTTP on {SERVER_HOST}:{SERVER_PORT}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
