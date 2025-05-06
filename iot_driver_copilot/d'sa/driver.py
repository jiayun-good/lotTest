import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import urllib.parse
import xml.etree.ElementTree as ET

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def get_env(key, default=None, required=False):
    value = os.environ.get(key, default)
    if required and value is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return value

DEVICE_IP = get_env("DEVICE_IP", required=True)
DEVICE_PORT = int(get_env("DEVICE_PORT", "8001"))
SERVER_HOST = get_env("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(get_env("SERVER_PORT", "8080"))

class DeviceConnection:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)
        self.lock = threading.Lock()

    def fetch_data_xml(self):
        import http.client
        conn = http.client.HTTPConnection(self.ip, self.port, timeout=5)
        try:
            conn.request("GET", "/data")
            resp = conn.getresponse()
            if resp.status == 200:
                data = resp.read()
                return data
            else:
                return None
        finally:
            conn.close()

    def send_command_xml(self, xml_payload):
        import http.client
        conn = http.client.HTTPConnection(self.ip, self.port, timeout=5)
        try:
            conn.request("POST", "/cmd", body=xml_payload, headers={"Content-Type": "application/xml"})
            resp = conn.getresponse()
            data = resp.read()
            return resp.status, data
        finally:
            conn.close()

class IoTHTTPRequestHandler(BaseHTTPRequestHandler):
    devconn = DeviceConnection(DEVICE_IP, DEVICE_PORT)

    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), "utf-8"))
        elif parsed_path.path == "/data":
            # Fetch data from device and stream as XML over HTTP
            xml_data = self.devconn.fetch_data_xml()
            if xml_data:
                self._set_headers(200, "application/xml")
                self.wfile.write(xml_data)
            else:
                self._set_headers(502, "application/json")
                self.wfile.write(b'{"error": "Failed to fetch data from device"}')
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)
            # Validate XML payload
            try:
                ET.fromstring(post_body)
            except ET.ParseError:
                self._set_headers(400, "application/json")
                self.wfile.write(b'{"error": "Invalid XML payload"}')
                return
            status, resp_data = self.devconn.send_command_xml(post_body)
            self._set_headers(status, "application/xml")
            self.wfile.write(resp_data)
        else:
            self._set_headers(404, "application/json")
            self.wfile.write(b'{"error": "Not found"}')

    def log_message(self, format, *args):
        # Suppress default logging
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTHTTPRequestHandler)
    print(f"Serving on {SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()