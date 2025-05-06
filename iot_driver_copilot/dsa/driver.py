import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DEVICE_INFO = {
    "device_name": os.environ.get("DEVICE_NAME", "dsa"),
    "device_model": os.environ.get("DEVICE_MODEL", "dsa"),
    "manufacturer": os.environ.get("DEVICE_MANUFACTURER", ""),
    "device_type": os.environ.get("DEVICE_TYPE", "")
}

def check_device_health():
    # As there is no protocol or actual connectivity to check, always return healthy
    return {"status": "healthy"}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode("utf-8"))
        elif self.path == "/health":
            self._set_headers()
            self.wfile.write(json.dumps(check_device_health()).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

def run(server_class=HTTPServer, handler_class=DeviceHTTPRequestHandler):
    server_host = os.environ.get("HTTP_SERVER_HOST", "0.0.0.0")
    server_port = int(os.environ.get("HTTP_SERVER_PORT", "8000"))
    server_address = (server_host, server_port)
    httpd = server_class(server_address, handler_class)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run()