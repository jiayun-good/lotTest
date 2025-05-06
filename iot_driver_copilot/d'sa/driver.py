import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import xml.etree.ElementTree as ET

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def fetch_device_data():
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as sock:
            # Protocol-specific request logic here (assuming a simple request)
            sock.sendall(b"<get_data />")
            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
            raw_xml = b"".join(chunks)
        return raw_xml.decode("utf-8")
    except Exception as e:
        return None

def send_device_command(xml_payload):
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as sock:
            sock.sendall(xml_payload.encode("utf-8"))
            chunks = []
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
            resp_xml = b"".join(chunks)
        return resp_xml.decode("utf-8")
    except Exception as e:
        return None

class IoTDeviceHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
            raw_xml = fetch_device_data()
            if raw_xml is None:
                self._set_headers(502)
                self.wfile.write(b'{"error": "Failed to retrieve data from device."}')
                return
            self._set_headers(200, "application/xml")
            self.wfile.write(raw_xml.encode("utf-8"))
        elif self.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(str.encode(str(DEVICE_INFO).replace("'", '"')))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode("utf-8")
            try:
                # Accept only XML payloads
                ET.fromstring(post_data)
            except Exception:
                self._set_headers(400)
                self.wfile.write(b'{"error": "Invalid XML payload."}')
                return
            resp_xml = send_device_command(post_data)
            if resp_xml is None:
                self._set_headers(502)
                self.wfile.write(b'{"error": "Failed to send command to device."}')
                return
            self._set_headers(200, "application/xml")
            self.wfile.write(resp_xml.encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), IoTDeviceHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()