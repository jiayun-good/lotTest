import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Load config from environment variables
DEVICE_IP = os.getenv('DEVICE_IP', '127.0.0.1')
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8080'))

# Dummy device info and state (simulate interaction with device)
DEVICE_INFO = {
    "device_name": "asdads",
    "device_model": "ads",
    "manufacturer": "asddas",
    "device_type": "asd",
    "primary_protocol": "asd"
}
DEVICE_STATE = {
    "asd": 42,  # Example data point
}

def fetch_device_data():
    # Simulate retrieval of device data (would be an asd protocol call)
    # Return as JSON-serializable dict
    return {
        "asd": DEVICE_STATE.get("asd", None)
    }

def send_device_command(cmd_payload):
    # Simulate sending command to device and update state
    # Would normally use the asd protocol to communicate
    if 'asd' in cmd_payload:
        DEVICE_STATE['asd'] = cmd_payload['asd']
        return {"status": "success", "message": "Command executed"}
    else:
        return {"status": "error", "message": "Invalid command payload"}

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/info":
            self._set_headers()
            response = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "primary_protocol": DEVICE_INFO["primary_protocol"]
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))

        elif parsed_path.path == "/data":
            self._set_headers()
            data = fetch_device_data()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode('utf-8'))
                result = send_device_command(payload)
                self._set_headers(200 if result["status"] == "success" else 400)
                self.wfile.write(json.dumps(result).encode('utf-8'))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=DeviceHTTPRequestHandler):
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = server_class(server_address, handler_class)
    print(f"Starting HTTP server at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == '__main__':
    run()