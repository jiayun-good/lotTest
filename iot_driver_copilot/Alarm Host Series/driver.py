import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Mock device "SDK" - Replace with actual SDK calls or binary protocol handling as needed.
class HikvisionAlarmHostDevice:
    def __init__(self, ip, port, username, password):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.fake_status = {
            "alarm_state": "normal",
            "zones": [{"zone": 1, "status": "ok"}, {"zone": 2, "status": "bypassed"}],
            "sensors": {"battery_voltage": 12.3, "water": 0, "dust": 1},
        }
        self.armed_subsystems = set()
        self.bypassed_zones = set()
        self.active_alarms = False

    def get_status(self):
        # In a real implementation, query the device via SDK/network protocol
        return self.fake_status

    def clear_alarm(self):
        # In a real implementation, send a clear alarm command to the device
        self.active_alarms = False
        return {"success": True, "message": "Alarms cleared."}

    def manage_subsystem(self, subsystem_id, action):
        # In a real implementation, send arm/disarm/clear command to the device
        if action == "arm":
            self.armed_subsystems.add(subsystem_id)
            return {"success": True, "message": f"Subsystem {subsystem_id} armed."}
        elif action == "disarm":
            self.armed_subsystems.discard(subsystem_id)
            return {"success": True, "message": f"Subsystem {subsystem_id} disarmed."}
        elif action == "clear_alarm":
            self.active_alarms = False
            return {"success": True, "message": f"Alarms for subsystem {subsystem_id} cleared."}
        else:
            return {"success": False, "error": "Invalid action"}

    def bypass_zone(self, zone_id, action):
        # In a real implementation, send bypass/unbypass command to the device
        if action == "bypass":
            self.bypassed_zones.add(zone_id)
            return {"success": True, "message": f"Zone {zone_id} bypassed."}
        elif action == "unbypass":
            self.bypassed_zones.discard(zone_id)
            return {"success": True, "message": f"Zone {zone_id} unbypassed."}
        else:
            return {"success": False, "error": "Invalid action"}

# Environment variable configuration
DEVICE_IP = os.getenv('DEVICE_IP', '192.168.1.64')
DEVICE_PORT = int(os.getenv('DEVICE_PORT', '8000'))
DEVICE_USERNAME = os.getenv('DEVICE_USERNAME', 'admin')
DEVICE_PASSWORD = os.getenv('DEVICE_PASSWORD', '12345')
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8080'))

device = HikvisionAlarmHostDevice(
    ip=DEVICE_IP,
    port=DEVICE_PORT,
    username=DEVICE_USERNAME,
    password=DEVICE_PASSWORD
)

class AlarmHostHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, response_data, status_code=200):
        resp = json.dumps(response_data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def do_GET(self):
        if self.path == '/status':
            status = device.get_status()
            self._send_json(status)
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        content_len = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_len) if content_len > 0 else b''
        try:
            body = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception:
            self._send_json({"error": "Malformed JSON"}, status_code=400)
            return

        if self.path == '/alarm/clear':
            res = device.clear_alarm()
            self._send_json(res)
        elif self.path == '/subsys':
            subsystem_id = body.get('subsystem_id')
            action = body.get('action')
            if not subsystem_id or not action:
                self._send_json({"error": "Missing 'subsystem_id' or 'action' in body"}, status_code=400)
                return
            res = device.manage_subsystem(subsystem_id, action)
            self._send_json(res)
        elif self.path == '/zone/bypass':
            zone_id = body.get('zone_id')
            action = body.get('action')
            if not zone_id or not action:
                self._send_json({"error": "Missing 'zone_id' or 'action' in body"}, status_code=400)
                return
            res = device.bypass_zone(zone_id, action)
            self._send_json(res)
        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):
        return  # Silence the default logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, AlarmHostHTTPRequestHandler)
    print(f"Alarm Host HTTP API server running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()