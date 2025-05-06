import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# ========== Configuration from Environment Variables ==========
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# ========== Device Info ==========
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# ================= Device Communication Layer =================

def get_device_data():
    """
    Connects to the device over TCP, requests current data, and returns XML string.
    """
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            # For demonstration, we assume the protocol expects sending "GET_DATA\n"
            sock.sendall(b"GET_DATA\n")
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode("utf-8")
    except Exception as e:
        return f"<error>{str(e)}</error>"

def send_device_command(xml_payload):
    """
    Connects to the device over TCP, sends command in XML, and returns XML response.
    """
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(5)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            # Send command as XML
            sock.sendall(xml_payload.encode('utf-8'))
            sock.shutdown(socketserver.socket.SHUT_WR)
            data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode("utf-8")
    except Exception as e:
        return f"<error>{str(e)}</error>"

# ========== HTTP Server Handler ==========

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/xml"):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            self._set_headers("application/xml")
            xml_data = get_device_data()
            self.wfile.write(xml_data.encode("utf-8"))

        elif self.path == '/info':
            self._set_headers("application/json")
            info = {
                "device_name": DEVICE_INFO["device_name"],
                "device_model": DEVICE_INFO["device_model"],
                "manufacturer": DEVICE_INFO["manufacturer"],
                "device_type": DEVICE_INFO["device_type"],
            }
            import json
            self.wfile.write(json.dumps(info).encode("utf-8"))
        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            if self.headers.get('Content-Type', '').startswith('application/xml'):
                xml_payload = post_data.decode('utf-8')
            else:
                # If not XML, wrap the payload in a simple XML element
                xml_payload = f"<command>{post_data.decode('utf-8')}</command>"
            response_xml = send_device_command(xml_payload)
            self._set_headers("application/xml")
            self.wfile.write(response_xml.encode("utf-8"))
        else:
            self.send_error(404, "Not found")

    def log_message(self, format, *args):
        return  # Silent logging

# ========== Threaded HTTP Server ==========
class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    httpd = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()