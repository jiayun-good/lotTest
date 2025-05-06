import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DEVICE_INFO = {
    "device_name": os.environ.get("DEVICE_NAME", "dsa"),
    "device_model": os.environ.get("DEVICE_MODEL", "dsa"),
    "manufacturer": os.environ.get("DEVICE_MANUFACTURER", ""),
    "device_type": os.environ.get("DEVICE_TYPE", "")
}

class DsaHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers()
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        elif self.path == '/health':
            # Health check: always 'ok', can be extended for real device checks
            self._set_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode('utf-8'))

def run():
    server_host = os.environ.get("SERVER_HOST", "0.0.0.0")
    server_port = int(os.environ.get("SERVER_PORT", "8080"))
    httpd = HTTPServer((server_host, server_port), DsaHTTPRequestHandler)
    httpd.serve_forever()

if __name__ == '__main__':
    run()
