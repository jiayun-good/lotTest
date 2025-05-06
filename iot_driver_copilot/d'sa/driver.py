import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# Configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device static info
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simple XML protocol simulation: connect, send XML, receive XML
def fetch_device_data():
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((DEVICE_IP, DEVICE_PORT))
            # Example XML request to get data points
            request_xml = '<GetDataPoints/>'
            s.sendall(request_xml.encode('utf-8'))
            response = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            return response.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

def send_device_command(command_xml):
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((DEVICE_IP, DEVICE_PORT))
            s.sendall(command_xml.encode('utf-8'))
            response = b''
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
            return response.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

class SimpleIoTHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/data":
            self._set_headers()
            xml_data = fetch_device_data()
            self.wfile.write(xml_data.encode('utf-8'))
        elif self.path == "/info":
            self._set_headers(content_type="application/json")
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Assume posted data is XML, pass directly to device
                command_xml = post_data.decode('utf-8')
                response_xml = send_device_command(command_xml)
                self._set_headers()
                self.wfile.write(response_xml.encode('utf-8'))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(f"<error>{str(e)}</error>".encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'Not Found')

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, SimpleIoTHandler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()