import os
import csv
import io
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

DEVICE_NAME = os.environ.get("DEVICE_NAME", "asd")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "sda")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "sad")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "asd")
DATA_POINTS = os.environ.get("DATA_POINTS", "sad")
COMMANDS = os.environ.get("COMMANDS", "sad")
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated device state and data
device_status = {"operational": True}
device_data_points = ["temperature", "humidity", "status"]
device_data = {
    "temperature": "23.5",
    "humidity": "56",
    "status": "OK"
}
# Lock for thread safety
device_lock = threading.Lock()

def get_device_info():
    return {
        "device_name": DEVICE_NAME,
        "device_model": DEVICE_MODEL,
        "manufacturer": DEVICE_MANUFACTURER,
        "device_type": DEVICE_TYPE,
        "status": "online" if device_status["operational"] else "offline"
    }

def get_device_csv():
    # Simulate fetching data from device (replace with real protocol communication as needed)
    with device_lock:
        output = io.StringIO()
        writer = csv.writer(output)
        # Write header and row
        writer.writerow(device_data_points)
        writer.writerow([device_data.get(point, "") for point in device_data_points])
        return output.getvalue()


def handle_device_command(command):
    # Simulate command processing (replace with real protocol communication as needed)
    with device_lock:
        if command == "start":
            device_status["operational"] = True
            device_data["status"] = "OK"
        elif command == "stop":
            device_status["operational"] = False
            device_data["status"] = "Stopped"
        elif command == "diagnostic":
            return {"result": "All systems nominal"}
        else:
            return {"error": "Unknown command"}
    return {"result": "Command executed"}


class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            info = get_device_info()
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif self.path == "/data":
            self._set_headers(content_type="text/csv")
            csv_data = get_device_csv()
            self.wfile.write(csv_data.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(post_data)
                command = data.get("command")
                if not command:
                    raise ValueError
            except Exception:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Invalid command format"}).encode("utf-8"))
                return
            result = handle_device_command(command)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

def run_server():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running at http://{SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()