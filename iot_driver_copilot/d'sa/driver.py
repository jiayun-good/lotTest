import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET

# Device Info from environment variables
DEVICE_NAME = os.environ.get('DEVICE_NAME', "d'sa")
DEVICE_MODEL = os.environ.get('DEVICE_MODEL', "dsad'sa")
DEVICE_MANUFACTURER = os.environ.get('DEVICE_MANUFACTURER', "dasdasdas")
DEVICE_TYPE = os.environ.get('DEVICE_TYPE', "dsa")
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))  # Port for device protocol connection
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

class DeviceProtocolClient:
    """
    Simulates communication with a device over a custom (here named 'dsad') protocol.
    Reads and writes XML formatted data over TCP.
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_data(self):
        # Connect to device, send a request, get XML data points/status
        import socket
        with socket.create_connection((self.ip, self.port), timeout=5) as sock:
            # Send a request for data (protocol specifics would be needed in reality)
            sock.sendall(b"<request type='data'/>")
            data = self._recv_all(sock)
            return data.decode('utf-8')

    def send_command(self, xml_payload):
        import socket
        with socket.create_connection((self.ip, self.port), timeout=5) as sock:
            # Send the XML-formatted command payload
            sock.sendall(xml_payload.encode('utf-8'))
            resp = self._recv_all(sock)
            return resp.decode('utf-8')

    def _recv_all(self, sock):
        # Read until socket closes (very basic, for XML payloads)
        buffer = b""
        while True:
            part = sock.recv(4096)
            if not part:
                break
            buffer += part
        return buffer

device_client = DeviceProtocolClient(DEVICE_IP, DEVICE_PORT)

class DriverHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type='application/xml'):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            try:
                xml_data = device_client.get_data()
                self._set_headers(200, 'application/xml')
                self.wfile.write(xml_data.encode('utf-8'))
            except Exception as e:
                self._set_headers(502, 'text/plain')
                self.wfile.write(f'Error connecting to device: {e}'.encode('utf-8'))
        elif self.path == '/info':
            info = {
                'device_name': DEVICE_NAME,
                'device_model': DEVICE_MODEL,
                'manufacturer': DEVICE_MANUFACTURER,
                'device_type': DEVICE_TYPE
            }
            root = ET.Element('device_info')
            for k, v in info.items():
                ET.SubElement(root, k).text = v
            xml_str = ET.tostring(root, encoding='utf-8', method='xml')
            self._set_headers(200, 'application/xml')
            self.wfile.write(xml_str)
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                # Assume the posted data is XML directly
                xml_payload = body.decode('utf-8')
                resp = device_client.send_command(xml_payload)
                self._set_headers(200, 'application/xml')
                self.wfile.write(resp.encode('utf-8'))
            except Exception as e:
                self._set_headers(502, 'text/plain')
                self.wfile.write(f'Error sending command to device: {e}'.encode('utf-8'))
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        # Override to disable default logging to stderr
        pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DriverHTTPRequestHandler)
    print(f"Driver HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()