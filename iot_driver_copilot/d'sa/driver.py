import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import xml.etree.ElementTree as ET

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Environment Variables for Configuration
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))  # dsad protocol port
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Function to fetch data from device via "dsad" protocol (TCP socket, XML payloads)
def fetch_device_data():
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(b"<get_data />\n")
            buf = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                if b"</data>" in buf or b"</root>" in buf:
                    break
            return buf.decode("utf-8", errors="ignore")
    except Exception as e:
        return f"<error>{str(e)}</error>"

# Function to send a command to the device
def send_device_command(xml_cmd):
    try:
        with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as s:
            s.sendall(xml_cmd.encode("utf-8") + b"\n")
            buf = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                buf += chunk
                if b"</response>" in buf or b"</root>" in buf:
                    break
            return buf.decode("utf-8", errors="ignore")
    except Exception as e:
        return f"<error>{str(e)}</error>"

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/xml"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            resp = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"]
            }
            self.wfile.write(str(resp).replace("'", '"').encode("utf-8"))
        elif self.path == "/data":
            self._set_headers(200, "application/xml")
            data = fetch_device_data()
            self.wfile.write(data.encode("utf-8"))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Expecting XML
                ET.fromstring(post_data.decode("utf-8"))
                xml_cmd = post_data.decode("utf-8")
            except Exception as e:
                self._set_headers(400, "application/xml")
                self.wfile.write(f"<error>Invalid XML: {str(e)}</error>".encode("utf-8"))
                return
            result = send_device_command(xml_cmd)
            self._set_headers(200, "application/xml")
            self.wfile.write(result.encode("utf-8"))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

def run_server():
    httpd = HTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP server started on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()