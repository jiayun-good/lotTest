import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

DEVICE_INFO = {
    "device_name": os.getenv("DEVICE_NAME", "dsa"),
    "device_model": os.getenv("DEVICE_MODEL", "dsa"),
    "manufacturer": os.getenv("DEVICE_MANUFACTURER", ""),
    "device_type": os.getenv("DEVICE_TYPE", "")
}

class DsaHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(json.dumps({
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"]
            }).encode("utf-8"))
        elif self.path == "/health":
            # Here we just return healthy, as there is no device protocol to check
            self._set_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "reachable": True
            }).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

def run():
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    server = HTTPServer((host, port), DsaHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

if __name__ == "__main__":
    run()
