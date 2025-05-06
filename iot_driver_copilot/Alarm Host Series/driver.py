import os
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "8000"))
DEVICE_USER = os.environ.get("DEVICE_USER", "admin")
DEVICE_PASS = os.environ.get("DEVICE_PASS", "")
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Simulated Device State (replace with actual SDK/protocol integration)
device_state = {
    "alarm_state": "inactive",
    "zones": {
        "1": {"status": "normal", "bypassed": False},
        "2": {"status": "alarm", "bypassed": False},
        "3": {"status": "normal", "bypassed": True}
    },
    "subsystems": {
        "A": {"armed": False, "alarm": False},
        "B": {"armed": True, "alarm": True}
    },
    "battery_voltage": 12.7,
    "sensors": {
        "water": 0,
        "dust": 5,
        "noise": 20,
        "environmental": {"temp": 24.2, "humidity": 55}
    }
}

lock = threading.Lock()

class AlarmHostDevice:
    def clear_alarm(self):
        with lock:
            device_state["alarm_state"] = "inactive"
            for k in device_state["subsystems"]:
                device_state["subsystems"][k]["alarm"] = False
            return True

    def get_status(self):
        with lock:
            return {
                "alarm_state": device_state["alarm_state"],
                "zones": device_state["zones"],
                "subsystems": device_state["subsystems"],
                "battery_voltage": device_state["battery_voltage"],
                "sensors": device_state["sensors"]
            }

    def bypass_zone(self, zone_id, bypass):
        with lock:
            if zone_id in device_state["zones"]:
                device_state["zones"][zone_id]["bypassed"] = bool(bypass)
                return True
            return False

    def manage_subsystem(self, subsys_id, action):
        with lock:
            subsys = device_state["subsystems"].get(subsys_id)
            if not subsys:
                return False
            if action == "arm":
                subsys["armed"] = True
            elif action == "disarm":
                subsys["armed"] = False
            elif action == "clear_alarm":
                subsys["alarm"] = False
            else:
                return False
            return True

device = AlarmHostDevice()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _parse_post(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        content_type = self.headers.get('Content-Type', "")
        raw = self.rfile.read(content_length)
        if content_type.startswith("application/json"):
            try:
                return json.loads(raw)
            except Exception:
                return {}
        elif content_type.startswith("application/x-www-form-urlencoded"):
            return {k: v[0] for k, v in parse_qs(raw.decode()).items()}
        else:
            return {}

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/status":
            status = device.get_status()
            self._send_json({
                "success": True,
                "data": status
            })
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        # /alarm/clear
        if parsed.path == "/alarm/clear":
            ok = device.clear_alarm()
            self._send_json({"success": ok})

        # /zone/bypass
        elif parsed.path == "/zone/bypass":
            data = self._parse_post()
            zone_id = data.get("zone_id")
            bypass = data.get("bypass")
            if zone_id is None or bypass is None:
                self._send_json({"success": False, "error": "Missing zone_id or bypass"}, status=400)
                return
            try:
                bypass = bool(int(bypass)) if isinstance(bypass, str) else bool(bypass)
            except Exception:
                self._send_json({"success": False, "error": "Invalid bypass value"}, status=400)
                return
            ok = device.bypass_zone(str(zone_id), bypass)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"success": False, "error": "Zone not found"}, status=404)

        # /subsys
        elif parsed.path == "/subsys":
            data = self._parse_post()
            subsys_id = data.get("subsys_id")
            action = data.get("action")
            if not subsys_id or not action:
                self._send_json({"success": False, "error": "Missing subsys_id or action"}, status=400)
                return
            ok = device.manage_subsystem(str(subsys_id), action)
            if ok:
                self._send_json({"success": True})
            else:
                self._send_json({"success": False, "error": "Invalid subsystem or action"}, status=400)

        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        # Optional: comment out to silence log or redirect elsewhere
        pass

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f"Alarm Host HTTP driver started at http://{SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()