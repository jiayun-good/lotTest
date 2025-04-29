import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Device communication simulation (replace with real protocol logic)
class TttDeviceClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def get_data_points(self):
        # Simulate retrieving device data
        return {
            "temperature": 23.5,
            "humidity": 54,
            "status": "ok"
        }

    def send_command(self, command_payload):
        # Simulate sending a command to the device
        if "action" in command_payload:
            return {"result": "success", "executed": command_payload["action"]}
        return {"result": "error", "reason": "invalid command"}

# HTTP Handler
class DriverHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/data":
            try:
                data = self.server.device_client.get_data_points()
                self._send_json({"data": data})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
        else:
            self._send_json({"error": "Not found"}, status=404)

    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                payload = json.loads(post_data.decode('utf-8'))
                result = self.server.device_client.send_command(payload)
                self._send_json(result)
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
        else:
            self._send_json({"error": "Not found"}, status=404)

class DriverHTTPServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass, device_client):
        super().__init__(server_address, RequestHandlerClass)
        self.device_client = device_client

def main():
    # Read environment variables for configuration
    DEVICE_HOST = os.environ.get('DEVICE_HOST', '127.0.0.1')
    DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
    SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
    SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

    # Initialize device client
    device_client = TttDeviceClient(DEVICE_HOST, DEVICE_PORT)

    # Start HTTP server
    server = DriverHTTPServer((SERVER_HOST, SERVER_PORT), DriverHTTPRequestHandler, device_client)
    try:
        print(f"Driver HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == '__main__':
    main()