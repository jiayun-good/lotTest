import os
import threading
import http.server
import socketserver
import socket
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs

# Environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_ADAS_PORT = int(os.environ.get('DEVICE_ADAS_PORT', '7000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulated protocol: ADAS (custom, XML over TCP)
class AdasDeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def send_command(self, command):
        req_xml = f"<command>{command}</command>"
        with socket.create_connection((self.ip, self.port), timeout=5) as sock:
            sock.sendall(req_xml.encode())
            resp = self._recv_all(sock)
        return resp

    def get_data(self):
        req_xml = "<get_data/>"
        with socket.create_connection((self.ip, self.port), timeout=5) as sock:
            sock.sendall(req_xml.encode())
            resp = self._recv_all(sock)
        return resp

    def _recv_all(self, sock):
        chunks = []
        sock.settimeout(2)
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
        except socket.timeout:
            pass
        return b''.join(chunks).decode(errors='ignore')

adas_client = AdasDeviceClient(DEVICE_IP, DEVICE_ADAS_PORT)

# Device static info
DEVICE_INFO = {
    "device_name": "tes",
    "device_model": "sdssd",
    "manufacturer": "ss",
    "device_type": "sd",
    "primary_protocol": "adas"
}

class Handler(http.server.BaseHTTPRequestHandler):

    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/info':
            self._set_headers()
            self.wfile.write(bytes(str(DEVICE_INFO), 'utf-8'))
        elif parsed.path == '/data':
            xml_data = adas_client.get_data()
            self._set_headers(content_type="application/xml")
            self.wfile.write(xml_data.encode())
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode()
            try:
                tree = ET.fromstring(post_data)
                cmd = tree.text if tree.tag == "command" else post_data
            except Exception:
                cmd = post_data
            resp_xml = adas_client.send_command(cmd)
            self._set_headers(content_type="application/xml")
            self.wfile.write(resp_xml.encode())
        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run_server():
    with ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), Handler) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()