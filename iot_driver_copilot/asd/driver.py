import os
import csv
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json

# Device info from environment variables or defaults
DEVICE_NAME = os.environ.get('DEVICE_NAME', 'asd')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'sda')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', 'sad')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'asd')

# Device connection info from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))  # dsa protocol port, configurable
# HTTP Server config
HTTP_HOST = os.environ.get('HTTP_HOST', '0.0.0.0')
HTTP_PORT = int(os.environ.get('HTTP_PORT', '8080'))

# Dummy in-memory data to mimic device data for /data
DEVICE_DATA_POINTS = [
    {'timestamp': '2024-06-10T12:00:00Z', 'value1': 23, 'value2': 51},
    {'timestamp': '2024-06-10T12:00:01Z', 'value1': 24, 'value2': 52},
    {'timestamp': '2024-06-10T12:00:02Z', 'value1': 25, 'value2': 53}
]

# --- Simulated DSA Protocol Communication ---
def get_device_data_from_dsa():
    """
    Simulate connecting to a device via DSA protocol (TCP, custom).
    For real device: connect to DEVICE_IP:DEVICE_PORT and get data.
    Here, just yield the dummy DEVICE_DATA_POINTS as CSV lines.
    """
    # In a real driver, here you'd have socket code like:
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((DEVICE_IP, DEVICE_PORT))
    # s.send(b"GET DATA\n")
    # while True:
    #     chunk = s.recv(4096)
    #     yield chunk
    # For this simulation, just stream the dummy data as CSV.
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['timestamp', 'value1', 'value2'])
    writer.writeheader()
    for row in DEVICE_DATA_POINTS:
        writer.writerow(row)
    yield output.getvalue()
    output.close()

def send_command_to_device_dsa(command):
    """
    Simulate sending a command to the device via DSA. In real world, use sockets.
    Returns a dict with result info.
    """
    # Real code would send command over socket and read response.
    # For this simulation, just echo the command back.
    return {
        'status': 'success',
        'command_sent': command,
        'message': f'Command "{command}" sent to device at {DEVICE_IP}:{DEVICE_PORT}'
    }

# --- HTTP Handler ---
class DsaDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": DEVICE_MANUFACTURER,
                "device_type": DEVICE_TYPE
            }
            self.wfile.write(json.dumps(info).encode())
        elif self.path == "/data":
            self._set_headers(200, "text/csv")
            for data_chunk in get_device_data_from_dsa():
                self.wfile.write(data_chunk.encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                cmd_json = json.loads(body)
                command = cmd_json.get("command", "")
                if not command:
                    raise ValueError("Missing 'command' field")
                result = send_command_to_device_dsa(command)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as ex:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(ex)}).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

# --- HTTP Server Thread ---
class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((HTTP_HOST, HTTP_PORT), DsaDeviceHTTPRequestHandler)
    print(f"DSA HTTP Device Driver running at http://{HTTP_HOST}:{HTTP_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()