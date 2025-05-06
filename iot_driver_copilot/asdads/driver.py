import os
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

# Device Configuration from Environment Variables
DEVICE_IP = os.getenv('DEVICE_IP', '127.0.0.1')
SERVER_HOST = os.getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.getenv('SERVER_PORT', '8080'))

# Dummy device state for simulation
device_state = {
    "asd": 0  # Example data point
}

# Dummy device info
device_info = {
    "device_name": "asdads",
    "device_model": "ads",
    "manufacturer": "asddas",
    "device_type": "asd",
    "connection_protocol": "asd"
}

# Simulated communication with device
def get_device_data():
    # In a real driver, replace with code to poll/read from device
    return {
        "asd": device_state["asd"]
    }

def send_device_command(cmd_payload):
    # In a real driver, translate cmd_payload to device protocol and send
    # For simulation, we expect {"asd": some_value}
    if "asd" in cmd_payload:
        device_state["asd"] = cmd_payload["asd"]
        return True
    return False

class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers_json(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
    
    def _set_headers_text(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/info":
            self._set_headers_json()
            info = {
                "device_name": device_info["device_name"],
                "device_model": device_info["device_model"],
                "manufacturer": device_info["manufacturer"],
                "connection_protocol": device_info["connection_protocol"]
            }
            self.wfile.write(json.dumps(info).encode())
        elif parsed_path.path == "/data":
            self._set_headers_json()
            data = get_device_data()
            self.wfile.write(json.dumps(data).encode())
        else:
            self._set_headers_json(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
    
    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                payload = json.loads(body.decode())
                if send_device_command(payload):
                    self._set_headers_json()
                    self.wfile.write(json.dumps({"result": "success"}).encode())
                else:
                    self._set_headers_json(400)
                    self.wfile.write(json.dumps({"error": "Invalid command"}).encode())
            except Exception as e:
                self._set_headers_json(400)
                self.wfile.write(json.dumps({"error": "Malformed JSON or invalid payload"}).encode())
        else:
            self._set_headers_json(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, IoTDeviceHTTPRequestHandler)
    print(f"Starting HTTP server on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()