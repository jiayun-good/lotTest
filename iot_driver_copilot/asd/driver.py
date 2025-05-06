import os
import csv
import io
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Device info from environment variables
DEVICE_NAME = os.environ.get('DEVICE_NAME', 'asd')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'sda')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', 'sad')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'asd')

# Device connection info
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))

# HTTP server configuration
HTTP_HOST = os.environ.get('HTTP_HOST', '0.0.0.0')
HTTP_PORT = int(os.environ.get('HTTP_PORT', '8080'))

# Simulated data points and commands for demo purposes
DATA_POINTS = [
    {'timestamp': '2024-06-01T10:00:00Z', 'value': 23.2},
    {'timestamp': '2024-06-01T10:01:00Z', 'value': 24.1},
    {'timestamp': '2024-06-01T10:02:00Z', 'value': 22.9},
]

SUPPORTED_COMMANDS = ['start', 'stop', 'diagnose']

# Simulate device protocol connection and data fetching
def fetch_device_csv_data():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['timestamp', 'value'])
    writer.writeheader()
    for row in DATA_POINTS:
        writer.writerow(row)
    return output.getvalue()

def send_device_command(cmd):
    if cmd not in SUPPORTED_COMMANDS:
        return {'status': 'error', 'message': f'Unknown command: {cmd}'}
    # Simulate success
    return {'status': 'success', 'command': cmd}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def send_json(self, obj, code=200):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/info':
            info = {
                'device_name': DEVICE_NAME,
                'device_model': DEVICE_MODEL,
                'manufacturer': DEVICE_MANUFACTURER,
                'device_type': DEVICE_TYPE
            }
            self.send_json(info)
        elif parsed.path == '/data':
            csv_data = fetch_device_csv_data()
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv')
            self.end_headers()
            self.wfile.write(csv_data.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(post_data)
            except Exception:
                self.send_json({'status': 'error', 'message': 'Invalid JSON'}, code=400)
                return
            cmd = data.get('command')
            if not cmd:
                self.send_json({'status': 'error', 'message': 'Missing command'}, code=400)
                return
            result = send_device_command(cmd)
            self.send_json(result)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not found')

def run():
    server_address = (HTTP_HOST, HTTP_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running at http://{HTTP_HOST}:{HTTP_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()