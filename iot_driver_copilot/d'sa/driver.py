import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import xml.etree.ElementTree as ET

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9001"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def fetch_device_data():
    """Simulate fetching XML data from the device over a raw TCP protocol."""
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as sock:
            # For demonstration, send a command to request data points/status
            sock.sendall(b"GET_DATA\n")
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            # Assume device responds with XML
            return data.decode("utf-8")
    except Exception as e:
        return f"<error>{str(e)}</error>"

def send_device_command(xml_payload):
    """Send a command to the device using the raw protocol and return the device's response."""
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as sock:
            sock.sendall(b"SEND_COMMAND\n")
            if xml_payload:
                sock.sendall(xml_payload.encode("utf-8"))
            sock.shutdown(socket.SHUT_WR)
            resp = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                resp += chunk
            return resp.decode("utf-8")
    except Exception as e:
        return f"<error>{str(e)}</error>"

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            xml_data = fetch_device_data()
            self.wfile.write(xml_data.encode("utf-8"))
        elif self.path == "/info":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b""
            # We expect XML payload
            xml_payload = post_data.decode("utf-8")
            # Optionally validate XML here
            try:
                ET.fromstring(xml_payload)  # Validate XML
                valid_xml = True
            except ET.ParseError:
                valid_xml = False

            if not valid_xml:
                self.send_response(400)
                self.send_header('Content-Type', 'application/xml')
                self.end_headers()
                self.wfile.write(b"<error>Invalid XML payload</error>")
                return

            response = send_device_command(xml_payload)
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(response.encode("utf-8"))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b"Not found")

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = HTTPServer(server_address, DeviceHTTPRequestHandler)
    print(f"Device HTTP driver running at http://{SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()