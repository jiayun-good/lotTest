import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket

DEVICE_INFO = {
    "device_name": os.getenv("DEVICE_NAME", "dsa"),
    "device_model": os.getenv("DEVICE_MODEL", "dsa"),
    "manufacturer": os.getenv("MANUFACTURER", ""),
    "device_type": os.getenv("DEVICE_TYPE", "")
}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._handle_info()
        elif self.path == '/health':
            self._handle_health()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

    def _handle_info(self):
        self._set_headers()
        self.wfile.write(json.dumps({
            "device_name": DEVICE_INFO["device_name"],
            "device_model": DEVICE_INFO["device_model"],
            "manufacturer": DEVICE_INFO["manufacturer"],
            "device_type": DEVICE_INFO["device_type"]
        }).encode('utf-8'))

    def _handle_health(self):
        self._set_headers()
        reachable = self._ping_device()
        self.wfile.write(json.dumps({
            "status": "online" if reachable else "offline"
        }).encode('utf-8'))

    def _ping_device(self):
        device_ip = os.getenv("DEVICE_IP")
        if not device_ip:
            return False
        try:
            with socket.create_connection((device_ip, int(os.getenv("DEVICE_PING_PORT", 80))), timeout=3):
                return True
        except Exception:
            return False

def run():
    server_host = os.getenv("SERVER_HOST", "0.0.0.0")
    server_port = int(os.getenv("SERVER_PORT", 8080))
    httpd = HTTPServer((server_host, server_port), DeviceHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run()