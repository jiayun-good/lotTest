import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Mock device communication (replace with real protocol logic as necessary)
class TTTDeviceClient:
    def __init__(self, device_ip, device_port, timeout=5):
        self.device_ip = device_ip
        self.device_port = device_port
        self.timeout = timeout

    def get_data_points(self):
        # Simulate fetching data points from the device
        return {"temperature": 23.5, "humidity": 60, "status": "ok"}

    def send_command(self, command):
        # Simulate sending a command to the device
        return {"success": True, "command": command}


class IoTHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, obj, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/data':
            data = self.server.device_client.get_data_points()
            self._send_json({"data_points": data})
        else:
            self.send_error(404, "Endpoint not found.")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)
            try:
                payload = json.loads(post_body.decode('utf-8'))
            except Exception:
                self._send_json({"error": "Invalid JSON."}, status=400)
                return
            if "command" not in payload:
                self._send_json({"error": "Missing 'command' field."}, status=400)
                return
            result = self.server.device_client.send_command(payload["command"])
            self._send_json(result)
        else:
            self.send_error(404, "Endpoint not found.")

    def log_message(self, format, *args):
        # Silence default http.server logging
        pass


def main():
    # Load configuration from environment variables
    DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
    DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
    SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

    device_client = TTTDeviceClient(DEVICE_IP, DEVICE_PORT)

    class CustomHTTPServer(HTTPServer):
        def __init__(self, server_address, RequestHandlerClass, device_client):
            super().__init__(server_address, RequestHandlerClass)
            self.device_client = device_client

    httpd = CustomHTTPServer((SERVER_HOST, SERVER_PORT), IoTHTTPRequestHandler, device_client)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == '__main__':
    main()