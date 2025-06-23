import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Load configuration from environment variables
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device configuration via environment
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '5000'))
DEVICE_NAME = os.environ.get('DEVICE_NAME', 'test1')

# For demonstration purposes, fake data/command handlers
def device_send_command(cmd_json):
    # Simulate sending a command to the device and getting a result
    # In a real driver, you would connect to the device (e.g., via TCP/HTTP/Serial)
    # and send the actual command, then read the response.
    # Here we just echo back the request as an 'ack'.
    return {
        "status": "success",
        "device": DEVICE_NAME,
        "command": cmd_json
    }

def device_get_data(query_params):
    # Simulate fetching data from the device
    # In a real driver, connect and request current data.
    # Here, we just return a stub.
    return {
        "device": DEVICE_NAME,
        "data": {
            "temperature": 24.5,
            "humidity": 56,
            "status": "OK"
        },
        "query": query_params
    }

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                cmd_json = json.loads(body.decode('utf-8'))
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
                return

            # Send command to device
            result = device_send_command(cmd_json)
            self._set_headers(200)
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/data':
            query = parse_qs(parsed_path.query)
            # Fetch data from device with query as parameter
            result = device_get_data(query)
            self._set_headers(200)
            self.wfile.write(json.dumps(result).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))

    def log_message(self, format, *args):
        # Disable default logging to stderr
        pass

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()