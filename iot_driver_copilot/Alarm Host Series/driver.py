import os
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Environment variable configuration
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '8000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))
DEVICE_USER = os.environ.get('DEVICE_USER', 'admin')
DEVICE_PASS = os.environ.get('DEVICE_PASS', '12345')

# Mocked device SDK communication
# In a real implementation, this would use actual SDK or socket protocol
class HikAlarmHostDevice:
    def __init__(self, ip, port, user, password):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password

    def get_status(self):
        # Simulate binary to structured data decode
        # Replace this with actual device communication
        return {
            "alarm_state": "armed",
            "zones": [
                {"id": 1, "status": "normal"},
                {"id": 2, "status": "bypassed"},
                {"id": 3, "status": "alarm"},
            ],
            "battery_voltage": 12.5,
            "sensor_readings": {
                "water": False,
                "dust": 10,
                "noise": 30,
                "environmental": {"temp": 21.5, "humidity": 40}
            },
            "device_time": "2024-06-05T12:00:00Z"
        }

    def clear_alarm(self):
        # Simulate clearing the alarm
        return {"success": True, "message": "Alarms cleared."}

    def subsystem_op(self, subsystem_id, action):
        # Simulate arming/disarming/clearing alarm for a subsystem
        if action not in ["arm", "disarm", "clear_alarm"]:
            return {"success": False, "message": "Invalid action"}
        return {"success": True, "subsystem_id": subsystem_id, "action": action, "message": f"Subsystem {subsystem_id} {action}ed."}

    def zone_bypass(self, zone_id, bypass):
        # Simulate bypassing or reinstating a zone
        return {"success": True, "zone_id": zone_id, "bypassed": bool(bypass), "message": f"Zone {zone_id} {'bypassed' if bypass else 'reinstated'}."}

# Instantiate device connection
device = HikAlarmHostDevice(DEVICE_IP, DEVICE_PORT, DEVICE_USER, DEVICE_PASS)

class SimpleAlarmHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

    def _parse_post_data(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
        except Exception:
            data = {}
        return data

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/status':
            self._set_headers()
            status = device.get_status()
            self.wfile.write(json.dumps(status).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        data = self._parse_post_data()

        if parsed_path.path == '/alarm/clear':
            result = device.clear_alarm()
            self._set_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        elif parsed_path.path == '/subsys':
            subsystem_id = data.get("subsystem_id")
            action = data.get("action")
            if subsystem_id is None or action is None:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "message": "Missing 'subsystem_id' or 'action'."}).encode('utf-8'))
                return
            result = device.subsystem_op(subsystem_id, action)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        elif parsed_path.path == '/zone/bypass':
            zone_id = data.get("zone_id")
            bypass = data.get("bypass")
            if zone_id is None or bypass is None:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "message": "Missing 'zone_id' or 'bypass'."}).encode('utf-8'))
                return
            result = device.zone_bypass(zone_id, bypass)
            self._set_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, SimpleAlarmHTTPRequestHandler)
    print(f"Alarm Host HTTP Server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()