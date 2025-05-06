import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

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

def get_device_data():
    # Simulate connecting to device via TCP socket and fetching XML data
    import socket
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as sock:
            sock.sendall(b"<get_data/>")
            received = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                received += chunk
        return received.decode()
    except Exception as e:
        return "<error>{}</error>".format(str(e))

def send_device_command(xml_payload):
    # Simulate sending a command in XML to the device via TCP socket
    import socket
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as sock:
            sock.sendall(xml_payload.encode())
            received = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                received += chunk
        return received.decode()
    except Exception as e:
        return "<error>{}</error>".format(str(e))

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers()
            self.wfile.write(bytes(str(DEVICE_INFO), "utf-8"))
        elif self.path == "/data":
            xml_str = get_device_data()
            # Convert XML to JSON-like dict for browser consumption
            try:
                root = ET.fromstring(xml_str)
                data = {root.tag: {child.tag: child.text for child in root}}
                import json
                self._set_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception:
                self._set_headers(502)
                self.wfile.write(bytes('{"error": "Invalid XML from device"}', "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                xml_payload = post_data.decode()
                # Validate XML
                ET.fromstring(xml_payload)
                response_xml = send_device_command(xml_payload)
                # Try to parse response and return as JSON
                try:
                    root = ET.fromstring(response_xml)
                    resp_data = {root.tag: {child.tag: child.text for child in root}}
                    import json
                    self._set_headers()
                    self.wfile.write(json.dumps(resp_data).encode())
                except Exception:
                    self._set_headers()
                    self.wfile.write(bytes(response_xml, "utf-8"))
            except Exception:
                self._set_headers(400)
                self.wfile.write(b'{"error": "Invalid XML payload"}')
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def log_message(self, format, *args):
        pass  # Suppress default logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run()