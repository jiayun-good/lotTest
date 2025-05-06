import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json

DEVICE_NAME = os.environ.get('DEVICE_NAME', 'asd')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'sda')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', 'sad')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'asd')

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))

SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Dummy device data and command simulation for illustration purposes
SIMULATED_DATA_POINTS = [
    ['timestamp', 'value1', 'value2'],
    ['2024-06-10T12:00:00Z', '23.4', '56.7'],
    ['2024-06-10T12:00:01Z', '23.5', '56.8'],
]

class DeviceConnection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_csv_data(self):
        # In a real driver, connect to the device and retrieve CSV data stream
        output = io.StringIO()
        writer = csv.writer(output)
        for row in SIMULATED_DATA_POINTS:
            writer.writerow(row)
        return output.getvalue()

    def send_command(self, command):
        # In a real driver, send command to device and return response
        # Simulate command response
        return {"status": "success", "command": command}

class Handler(BaseHTTPRequestHandler):
    device_conn = DeviceConnection(DEVICE_IP, DEVICE_PORT)

    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": DEVICE_MANUFACTURER,
                "device_type": DEVICE_TYPE,
            }
            self.wfile.write(json.dumps(info).encode('utf-8'))
        elif self.path == '/data':
            csv_data = self.device_conn.get_csv_data()
            self._set_headers(content_type="text/csv")
            self.wfile.write(csv_data.encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                command_data = json.loads(post_data.decode('utf-8'))
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode('utf-8'))
                return
            response = self.device_conn.send_command(command_data)
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, Handler)
    print(f"Starting HTTP server on {SERVER_HOST}:{SERVER_PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()