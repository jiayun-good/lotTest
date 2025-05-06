import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def fetch_device_xml_data():
    # Simulate TCP socket connection to the device to fetch XML data
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            request = b"<GetData></GetData>"
            sock.sendall(request)
            xml_data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                xml_data += chunk
            return xml_data.decode('utf-8')
    except Exception as e:
        return None

def send_device_xml_command(command_xml):
    # Simulate TCP socket connection to the device to send XML command and receive response
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((DEVICE_IP, DEVICE_PORT))
            sock.sendall(command_xml.encode('utf-8'))
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            return response.decode('utf-8')
    except Exception as e:
        return None

class ThreadingSimpleServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            xml_data = fetch_device_xml_data()
            if xml_data is None:
                self._set_headers(502, 'application/json')
                self.wfile.write(b'{"error": "Failed to connect to device"}')
                return
            self._set_headers(200, 'application/xml')
            self.wfile.write(xml_data.encode('utf-8'))
        elif self.path == '/info':
            self._set_headers(200, 'application/json')
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        else:
            self._set_headers(404, 'application/json')
            self.wfile.write(b'{"error":"Not found"}')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Expecting XML payload
                command_xml = post_data.decode('utf-8')
                # Basic XML validation
                try:
                    ET.fromstring(command_xml)
                except Exception:
                    self._set_headers(400, 'application/json')
                    self.wfile.write(b'{"error": "Invalid XML"}')
                    return
                response_xml = send_device_xml_command(command_xml)
                if response_xml is None:
                    self._set_headers(502, 'application/json')
                    self.wfile.write(b'{"error": "Failed to connect to device"}')
                    return
                self._set_headers(200, 'application/xml')
                self.wfile.write(response_xml.encode('utf-8'))
            except Exception:
                self._set_headers(500, 'application/json')
                self.wfile.write(b'{"error": "Internal server error"}')
        else:
            self._set_headers(404, 'application/json')
            self.wfile.write(b'{"error":"Not found"}')

def run_server():
    server = ThreadingSimpleServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"HTTP Server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    server.serve_forever()

if __name__ == '__main__':
    run_server()