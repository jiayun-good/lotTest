import os
import csv
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import time
import json

DEVICE_INFO = {
    "device_name": os.environ.get("DEVICE_NAME", "asd"),
    "device_model": os.environ.get("DEVICE_MODEL", "sda"),
    "manufacturer": os.environ.get("MANUFACTURER", "sad"),
    "device_type": os.environ.get("DEVICE_TYPE", "asd")
}

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DATA_TIMEOUT = float(os.environ.get("DATA_TIMEOUT", "2.0"))
CMD_TIMEOUT = float(os.environ.get("CMD_TIMEOUT", "2.0"))

def fetch_device_data():
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), DATA_TIMEOUT) as s:
            s.sendall(b'GET_DATA\n')
            buf = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
            return buf.decode("utf-8")
    except Exception:
        return ""

def send_device_command(cmd):
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), CMD_TIMEOUT) as s:
            s.sendall(f"CMD:{cmd}\n".encode("utf-8"))
            buf = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
            return buf.decode("utf-8")
    except Exception:
        return "ERROR"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/info":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode("utf-8"))
        elif self.path == "/data":
            self.send_response(200)
            self.send_header("Content-Type", "text/csv")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            data = fetch_device_data()
            if data:
                self.wfile.write(data.encode("utf-8"))
            else:
                # Return empty CSV
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(["error"])
                writer.writerow(["Could not retrieve data"])
                self.wfile.write(output.getvalue().encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                cmd = data.get("command")
                if not cmd:
                    raise ValueError("Missing 'command' field")
            except Exception:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid command"}).encode("utf-8"))
                return

            resp = send_device_command(cmd)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"response": resp}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), SimpleHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
