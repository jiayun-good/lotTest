import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

class DeviceConnectionError(Exception):
    pass

class DummyDeviceClient:
    # Simulated device client for 'dsad' protocol (XML over TCP)
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def _communicate(self, request_xml):
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(5)
            s.connect((self.ip, self.port))
            s.sendall(request_xml.encode('utf-8'))
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode('utf-8')
        except Exception as e:
            raise DeviceConnectionError(f"Could not connect to device: {e}")
        finally:
            s.close()

    def get_data(self):
        # Example request in 'dsad' protocol (XML)
        request_xml = "<Request><Action>GetData</Action></Request>"
        resp_xml = self._communicate(request_xml)
        # Validate XML
        try:
            root = ET.fromstring(resp_xml)
            return resp_xml
        except Exception:
            return "<Error>Malformed XML from device</Error>"

    def send_command(self, cmd_xml):
        # cmd_xml is expected to be a string containing XML
        resp_xml = self._communicate(cmd_xml)
        try:
            ET.fromstring(resp_xml)
            return resp_xml
        except Exception:
            return "<Error>Malformed XML from device</Error>"

    def get_info(self):
        # Simulate device info (hardcoded since it's static)
        info = {
            "device_name": "d'sa",
            "device_model": "dsad'sa",
            "manufacturer": "dasdasdas",
            "device_type": "dsa"
        }
        return info

device_client = DummyDeviceClient(DEVICE_IP, DEVICE_PORT)

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/xml"):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            try:
                xml_data = device_client.get_data()
                self._set_headers(200, "application/xml")
                self.wfile.write(xml_data.encode('utf-8'))
            except DeviceConnectionError as e:
                self._set_headers(502, "text/plain")
                self.wfile.write(str(e).encode('utf-8'))
        elif self.path == '/info':
            info = device_client.get_info()
            self._set_headers(200, "application/json")
            import json
            self.wfile.write(json.dumps(info).encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                # Assume client posts XML command
                xml_command = body.decode('utf-8')
                resp_xml = device_client.send_command(xml_command)
                self._set_headers(200, "application/xml")
                self.wfile.write(resp_xml.encode('utf-8'))
            except DeviceConnectionError as e:
                self._set_headers(502, "text/plain")
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        return  # Silence default logging

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"HTTP Server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

if __name__ == "__main__":
    run()