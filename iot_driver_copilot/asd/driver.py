import os
import csv
import io
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Environment variables for configuration
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Sample device info (could be loaded from env or config as needed)
DEVICE_INFO = {
    "device_name": os.environ.get('DEVICE_NAME', "asd"),
    "device_model": os.environ.get('DEVICE_MODEL', "sda"),
    "manufacturer": os.environ.get('DEVICE_MANUFACTURER', "sad"),
    "device_type": os.environ.get('DEVICE_TYPE', "asd")
}

# Simulated real-time CSV data generator (replace with actual device read logic)
class DeviceDataSimulator:
    def __init__(self):
        self.headers = ['timestamp', 'temperature', 'status']
        self.lock = threading.Lock()
        self.current_data = []
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._update_data)
        self._thread.daemon = True
        self._thread.start()

    def _update_data(self):
        while not self._stop_event.is_set():
            with self.lock:
                # Simulate some data points
                self.current_data = [
                    time.strftime('%Y-%m-%d %H:%M:%S'),
                    "%.2f" % (20.0 + 5.0 * (time.time() % 60) / 60),  # temp
                    "OK" if int(time.time()) % 2 == 0 else "WARN"
                ]
            time.sleep(1)

    def get_csv_row(self):
        with self.lock:
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(self.headers)
            writer.writerow(self.current_data)
            return output.getvalue()

    def stream_csv_rows(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.headers)
        yield output.getvalue()
        while not self._stop_event.is_set():
            with self.lock:
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow(self.current_data)
                yield output.getvalue()
            time.sleep(1)

    def stop(self):
        self._stop_event.set()
        self._thread.join()

device_data_simulator = DeviceDataSimulator()

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        data = json.dumps(obj).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == '/info':
            self._send_json(DEVICE_INFO)
        elif self.path == '/data':
            # Stream CSV data (browser or command line can consume)
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'close')
            self.end_headers()
            # Stream data rows (one header + repeated rows)
            try:
                for row in device_data_simulator.stream_csv_rows():
                    self.wfile.write(row.encode('utf-8'))
                    self.wfile.flush()
            except (ConnectionAbortedError, BrokenPipeError):
                return
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_json({'error': 'No command provided'}, status=400)
                return
            try:
                post_data = self.rfile.read(content_length)
                cmd = json.loads(post_data.decode('utf-8'))
            except Exception:
                self._send_json({'error': 'Invalid JSON'}, status=400)
                return
            # Simulate command processing (replace with real device logic)
            cmd_result = self._process_command(cmd)
            self._send_json(cmd_result)
        else:
            self.send_error(404, "Not Found")

    def _process_command(self, cmd):
        # Placeholder: echo command and pretend it's accepted
        # Extend this method to interact with the actual device via dsa protocol
        return {
            'received': cmd,
            'status': 'accepted'
        }

    def log_message(self, format, *args):
        # Suppress default logging for cleaner output
        return

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    try:
        print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        device_data_simulator.stop()
        server.server_close()

if __name__ == '__main__':
    run_server()