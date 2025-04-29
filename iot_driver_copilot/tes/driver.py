import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

DEVICE_NAME = os.environ.get("DEVICE_NAME", "tes")
DEVICE_MODEL = os.environ.get("DEVICE_MODEL", "tt")
DEVICE_MANUFACTURER = os.environ.get("DEVICE_MANUFACTURER", "ttt")
DEVICE_TYPE = os.environ.get("DEVICE_TYPE", "ttt")
PRIMARY_PROTOCOL = os.environ.get("PRIMARY_PROTOCOL", "ttt")
DATA_POINTS = os.environ.get("DATA_POINTS", "tt")
COMMANDS = os.environ.get("COMMANDS", "ttt")
DATA_FORMAT = os.environ.get("DATA_FORMAT", "XML")

SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))

DEVICE_USERNAME = os.environ.get("DEVICE_USERNAME", "admin")
DEVICE_PASSWORD = os.environ.get("DEVICE_PASSWORD", "admin")

DATA_ENDPOINT_PATH = os.environ.get("DEVICE_DATA_PATH", "/ttt/data")
COMMAND_ENDPOINT_PATH = os.environ.get("DEVICE_COMMAND_PATH", "/ttt/command")

class DeviceDriverHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_response(self, content, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(content.encode("utf-8") if isinstance(content, str) else content)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/info":
            self.handle_info()
        elif parsed.path == "/data":
            self.handle_data()
        else:
            self._send_response('{"error": "Not found"}', 404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/test":
            self.handle_test()
        else:
            self._send_response('{"error": "Not found"}', 404)

    def handle_info(self):
        info = {
            "device_name": DEVICE_NAME,
            "device_model": DEVICE_MODEL,
            "manufacturer": DEVICE_MANUFACTURER,
            "device_type": DEVICE_TYPE,
            "primary_protocol": PRIMARY_PROTOCOL,
            "data_points": DATA_POINTS,
            "commands": COMMANDS,
            "data_format": DATA_FORMAT,
            "ip": DEVICE_IP,
            "port": DEVICE_PORT,
        }
        import json
        self._send_response(json.dumps(info), 200, "application/json")

    def handle_data(self):
        try:
            data = self.device_get_data()
            self._send_response(data, 200, "application/xml")
        except Exception as e:
            self._send_response(f"<error>{str(e)}</error>", 500, "application/xml")

    def handle_test(self):
        try:
            test_result = self.device_test_command()
            self._send_response(test_result, 200, "application/xml")
        except Exception as e:
            self._send_response(f"<error>{str(e)}</error>", 500, "application/xml")

    def device_get_data(self):
        # Simulate fetching XML data from the device over TCP (or HTTP if appropriate)
        # Replace this with actual device protocol implementation
        # Here, we simulate a TCP connection that returns XML-formatted data
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((DEVICE_IP, DEVICE_PORT))
        # Protocol: send a command to get data (simulate with newline)
        s.sendall(b"GET_DATA\n")
        chunks = []
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            except socket.timeout:
                break
        s.close()
        xml_data = b"".join(chunks).decode("utf-8")
        # Validate XML and pretty print
        try:
            ET.fromstring(xml_data)
            return xml_data
        except ET.ParseError:
            # If the data is not valid XML, return an error XML
            return f"<error>Invalid XML data from device: {xml_data}</error>"

    def device_test_command(self):
        # Simulate sending a test command and getting XML response
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((DEVICE_IP, DEVICE_PORT))
        s.sendall(b"TEST_COMMAND\n")
        chunks = []
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
            except socket.timeout:
                break
        s.close()
        xml_data = b"".join(chunks).decode("utf-8")
        try:
            ET.fromstring(xml_data)
            return xml_data
        except ET.ParseError:
            return f"<error>Invalid XML data from device: {xml_data}</error>"

def run_server():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceDriverHTTPRequestHandler)
    print(f"Device driver HTTP server running on {SERVER_HOST}:{SERVER_PORT} ...")
    server.serve_forever()

if __name__ == "__main__":
    run_server()