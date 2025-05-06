import os
import csv
import io
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import json

# --- Configuration from Environment Variables ---
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))  # Port for the device's dsa protocol

# --- Device Static Info (could be dynamic if available) ---
DEVICE_INFO = {
    "device_name": "asd",
    "device_model": "sda",
    "manufacturer": "sad",
    "device_type": "asd"
}

# --- Simulated Device Protocol Handler ---
class DSADeviceClient:
    """
    Simulates connecting to the device using the proprietary 'dsa' protocol.
    Replace with actual protocol implementation as needed.
    """

    def __init__(self, device_ip, device_port):
        self.device_ip = device_ip
        self.device_port = device_port

    def get_realtime_csv(self):
        # Simulate fetching CSV data from the device.
        # In real implementation, connect to device and retrieve CSV.
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['timestamp', 'status', 'value'])
        writer.writerow(['2024-06-01T12:00:00Z', 'OK', '42'])
        writer.writerow(['2024-06-01T12:00:01Z', 'OK', '43'])
        return output.getvalue()

    def send_command(self, command):
        # Simulate sending a command to the device and getting a response.
        # In real implementation, send command via dsa protocol and return result.
        if command == "start":
            return {"result": "started"}
        elif command == "stop":
            return {"result": "stopped"}
        elif command == "diagnostic":
            return {"result": "diagnostic complete", "status": "OK"}
        else:
            return {"result": "unknown command"}

# --- HTTP Server Handler ---
class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    device_client = DSADeviceClient(DEVICE_IP, DEVICE_PORT)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        elif self.path == '/data':
            csv_data = self.device_client.get_realtime_csv()
            self._set_headers(content_type="text/csv")
            self.wfile.write(csv_data.encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            content_type = self.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                post_data = self.rfile.read(content_length).decode('utf-8')
                try:
                    payload = json.loads(post_data)
                    command = payload.get("command")
                    if not command:
                        self._set_headers(400)
                        self.wfile.write(json.dumps({"error": "Missing command"}).encode('utf-8'))
                        return
                    response = self.device_client.send_command(command)
                    self._set_headers()
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                except Exception as e:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            else:
                self._set_headers(415)
                self.wfile.write(json.dumps({"error": "Content-Type must be application/json"}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def log_message(self, format, *args):
        # Suppress standard logging to keep output clean
        return

# --- Threaded Server ---
class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()