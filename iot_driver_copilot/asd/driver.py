import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import threading

# Device info from environment or fallback
DEVICE_NAME = os.environ.get('DEVICE_NAME', 'asd')
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', 'sda')
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', 'sad')
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', 'asd')

# Device connection info
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))  # Port for raw protocol communication

# HTTP Server config
HTTP_HOST = os.environ.get('HTTP_HOST', '0.0.0.0')
HTTP_PORT = int(os.environ.get('HTTP_PORT', '8080'))

# Dummy function to simulate device data retrieval via the dsa protocol
def get_device_csv_data():
    # Simulate streaming/real-time data in CSV format
    # In a real driver, this would connect to DEVICE_IP:DEVICE_PORT via the actual dsa protocol
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['timestamp', 'param1', 'param2', 'param3'])
    writer.writerow(['2024-06-01T12:00:00Z', '42', '11.5', 'ACTIVE'])
    writer.writerow(['2024-06-01T12:00:01Z', '43', '11.4', 'ACTIVE'])
    return output.getvalue()

# Dummy function to simulate sending a command to the device via dsa protocol
def send_device_command(cmd):
    # Simulate processing a command
    # In a real driver, this would send the command to the device using dsa protocol and return the result
    return {
        'status': 'success',
        'command': cmd,
        'message': f'Command {cmd.get("action", "")} executed on device.'
    }

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    server_version = "DSADeviceHTTPDriver/1.0"

    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            info = {
                "device_name": DEVICE_NAME,
                "device_model": DEVICE_MODEL,
                "manufacturer": DEVICE_MANUFACTURER,
                "device_type": DEVICE_TYPE
            }
            self.wfile.write(json.dumps(info).encode('utf-8'))
        elif self.path == "/data":
            csv_data = get_device_csv_data()
            self._set_headers(content_type="text/csv")
            self.wfile.write(csv_data.encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                cmd = json.loads(body.decode('utf-8'))
                result = send_device_command(cmd)
                self._set_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid command format", "details": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode('utf-8'))

def run_server():
    server = ThreadedHTTPServer((HTTP_HOST, HTTP_PORT), DeviceHTTPRequestHandler)
    print(f"DSA Device HTTP Driver running at http://{HTTP_HOST}:{HTTP_PORT}/")
    server.serve_forever()

if __name__ == "__main__":
    run_server()