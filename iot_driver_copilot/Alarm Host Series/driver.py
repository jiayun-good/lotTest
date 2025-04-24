import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Environment variables for configuration
DEVICE_IP = os.environ.get("DEVICE_IP", "192.168.1.64")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "8000"))
DEVICE_USER = os.environ.get("DEVICE_USER", "admin")
DEVICE_PASS = os.environ.get("DEVICE_PASS", "12345")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated device backend communication (replace with SDK/protocol logic as needed)
def simulate_device_status():
    return {
        "alarm_state": "normal",
        "zones": [
            {"id": 1, "status": "armed", "tamper": False},
            {"id": 2, "status": "bypassed", "tamper": True},
        ],
        "sensors": {
            "battery_voltage": 12.7,
            "water": 0,
            "dust": 13,
            "noise": 41,
            "environmental": {"temperature": 26.2, "humidity": 44.1},
        },
        "subsystems": [
            {"id": "A", "status": "armed"},
            {"id": "B", "status": "disarmed"},
        ],
    }

def simulate_clear_alarm():
    return {"result": "success", "message": "Alarms cleared."}

def simulate_subsys_operation(subsystem_id, action):
    return {
        "result": "success",
        "subsystem_id": subsystem_id,
        "action": action,
        "message": f"Subsystem {subsystem_id} {action} operation performed."
    }

def simulate_zone_bypass(zone_id, bypass):
    return {
        "result": "success",
        "zone_id": zone_id,
        "bypass": bypass,
        "message": f"Zone {zone_id} bypass set to {bypass}."
    }

class AlarmHostHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/status":
            status_data = simulate_device_status()
            self._set_headers()
            self.wfile.write(json.dumps(status_data).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            if post_data:
                data = json.loads(post_data)
            else:
                data = {}
        except Exception:
            data = {}

        # /subsys endpoint
        if parsed_path.path == "/subsys":
            subsystem_id = data.get("subsystem_id")
            action = data.get("action")
            if not subsystem_id or not action:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "subsystem_id and action are required."}).encode('utf-8'))
                return
            response = simulate_subsys_operation(subsystem_id, action)
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        # /alarm/clear endpoint
        elif parsed_path.path == "/alarm/clear":
            response = simulate_clear_alarm()
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        # /zone/bypass endpoint
        elif parsed_path.path == "/zone/bypass":
            zone_id = data.get("zone_id")
            bypass = data.get("bypass")
            if zone_id is None or bypass is None:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "zone_id and bypass are required."}).encode('utf-8'))
                return
            response = simulate_zone_bypass(zone_id, bypass)
            self._set_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def log_message(self, format, *args):
        return  # Silence default logging

def run():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, AlarmHostHTTPRequestHandler)
    print(f"Alarm Host HTTP Driver running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run()
