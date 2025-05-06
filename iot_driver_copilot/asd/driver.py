import os
import csv
import io
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json

# Environment Variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "12345"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Device Info (static for this example)
DEVICE_INFO = {
    "device_name": "asd",
    "device_model": "sda",
    "manufacturer": "sad",
    "device_type": "asd"
}

# Simulated Device Data Source (thread-safe)
class DeviceDataSource:
    def __init__(self):
        self._lock = threading.Lock()
        self._data = [["timestamp", "value"]]
        self._running = True
        self._thread = threading.Thread(target=self._update_data, daemon=True)
        self._thread.start()

    def _update_data(self):
        while self._running:
            with self._lock:
                self._data.append([str(int(time.time())), str(self._generate_value())])
                # keep only latest 100 records
                if len(self._data) > 100:
                    self._data = self._data[-100:]
            time.sleep(1)

    def _generate_value(self):
        # Simulate device data
        return int(time.time()) % 100

    def get_csv_data(self):
        with self._lock:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerows(self._data)
            return output.getvalue()

    def add_command(self, cmd):
        # Simulate command processing
        with self._lock:
            self._data.append([str(int(time.time())), f"CMD:{cmd}"])
            if len(self._data) > 100:
                self._data = self._data[-100:]

    def stop(self):
        self._running = False

device_data_source = DeviceDataSource()

# HTTP Handler
class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/info":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode("utf-8"))
        elif self.path == "/data":
            csv_data = device_data_source.get_csv_data()
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv')
            self.send_header('Content-Disposition', 'inline; filename="device_data.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                cmd_data = json.loads(post_data.decode("utf-8"))
                cmd = cmd_data.get("command", "")
                device_data_source.add_command(cmd)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                resp = {"status": "ok", "command": cmd}
                self.wfile.write(json.dumps(resp).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return  # Suppress console logging

# Threaded HTTP Server
class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    try:
        print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        device_data_source.stop()
        server.server_close()

if __name__ == "__main__":
    run()