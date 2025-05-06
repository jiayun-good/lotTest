import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DEVICE_INFO = {
    "device_name": os.getenv("DEVICE_NAME", "dsa"),
    "device_model": os.getenv("DEVICE_MODEL", "dsa"),
    "manufacturer": os.getenv("DEVICE_MANUFACTURER", ""),
    "device_type": os.getenv("DEVICE_TYPE", "")
}

def check_device_health():
    # Simulate health check for device; always healthy for this generic example
    return {"status": "online", "detail": "Device is responsive"}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"]
            }
            self.wfile.write(json.dumps(info).encode("utf-8"))
        elif self.path == "/health":
            self._set_headers()
            health = check_device_health()
            self.wfile.write(json.dumps(health).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

def run():
    server_host = os.getenv("SERVER_HOST", "0.0.0.0")
    try:
        server_port = int(os.getenv("SERVER_PORT", "8080"))
    except ValueError:
        server_port = 8080

    httpd = HTTPServer((server_host, server_port), DeviceHTTPRequestHandler)
    print(f"Device HTTP server running at http://{server_host}:{server_port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run()