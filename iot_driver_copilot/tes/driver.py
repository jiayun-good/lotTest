import os
import threading
import socketserver
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# Environment Variables for configuration
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Dummy device info for demonstration
DEVICE_INFO = {
    "device_name": "tes",
    "device_model": "sdssd",
    "manufacturer": "ss",
    "device_type": "sd",
    "primary_protocol": "adas",
    "data_format": "XML"
}

# Simulate device communication via TCP socket (ADAS protocol placeholder)
def adas_send_command(command):
    try:
        with socketserver.socket.socket(socketserver.socket.AF_INET, socketserver.socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((DEVICE_IP, DEVICE_PORT))
            s.sendall(command.encode('utf-8'))
            data = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode('utf-8')
    except Exception as e:
        return f"<error>{str(e)}</error>"

def adas_get_data():
    # Simulate a data fetch command, for test purposes
    response = adas_send_command('GET_DATA')
    return response

def adas_execute_command(cmd):
    # Send the command to the device and return its response
    response = adas_send_command(cmd)
    return response

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/info':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(
                '{'
                f'"device_name":"{DEVICE_INFO["device_name"]}",'
                f'"device_model":"{DEVICE_INFO["device_model"]}",'
                f'"manufacturer":"{DEVICE_INFO["manufacturer"]}",'
                f'"device_type":"{DEVICE_INFO["device_type"]}",'
                f'"primary_protocol":"{DEVICE_INFO["primary_protocol"]}",'
                f'"data_format":"{DEVICE_INFO["data_format"]}",'
                f'"device_ip":"{DEVICE_IP}",'
                f'"device_port":{DEVICE_PORT}'
                '}', 'utf-8'
            ))
        elif parsed_path.path == '/data':
            xml_data = adas_get_data()
            # Proxy XML as HTTP stream
            self.send_response(200)
            self.send_header('Content-Type', 'application/xml')
            self.end_headers()
            self.wfile.write(xml_data.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expecting XML or simple command string
            try:
                try:
                    # Try parse as XML to extract command
                    root = ET.fromstring(post_data.decode('utf-8'))
                    cmd = root.findtext('command')
                    if not cmd:
                        cmd = post_data.decode('utf-8')
                except Exception:
                    # Not XML, treat as raw command
                    cmd = post_data.decode('utf-8')
                response = adas_execute_command(cmd)
                self.send_response(200)
                self.send_header('Content-Type', 'application/xml')
                self.end_headers()
                self.wfile.write(response.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"<error>{str(e)}</error>".encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        # Suppress logging to stderr
        pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Device HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()