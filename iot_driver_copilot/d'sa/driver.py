import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET

# Device Info (normally from device or constants)
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Helper: Get env vars with default fallback
def getenv(key, default=None, cast=str):
    val = os.environ.get(key, default)
    if val is not None and cast:
        try:
            return cast(val)
        except Exception:
            return default
    return val

# Configuration from environment variables
DEVICE_HOST = getenv('DEVICE_HOST', '127.0.0.1')
DEVICE_PORT = getenv('DEVICE_PORT', 9000, int)
SERVER_HOST = getenv('SERVER_HOST', '0.0.0.0')
SERVER_PORT = getenv('SERVER_PORT', 8080, int)

class DeviceProtocolError(Exception):
    pass

# Simulated Device Connection/Protocol (XML request/response)
class DSADDeviceClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def _send_xml(self, xml):
        import socket
        with socket.create_connection((self.host, self.port), timeout=5) as sock:
            sock.sendall(xml.encode('utf-8'))
            data = b""
            # Simple protocol: read until socket closes
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            return data.decode('utf-8')

    def fetch_data(self):
        # Simple GET-DATA XML
        xml_req = "<request><action>get_data</action></request>"
        xml_rsp = self._send_xml(xml_req)
        root = ET.fromstring(xml_rsp)
        # Convert XML to dict
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result

    def send_command(self, cmd_dict):
        xml_req = "<request><action>command</action>"
        for k, v in cmd_dict.items():
            xml_req += f"<{k}>{v}</{k}>"
        xml_req += "</request>"
        xml_rsp = self._send_xml(xml_req)
        root = ET.fromstring(xml_rsp)
        result = {}
        for child in root:
            result[child.tag] = child.text
        return result

# HTTP Handler
class IoTHTTPRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    device_client = DSADDeviceClient(DEVICE_HOST, DEVICE_PORT)

    def do_GET(self):
        if self.path == '/info':
            self.respond_json(200, DEVICE_INFO)
        elif self.path == '/data':
            try:
                data = self.device_client.fetch_data()
                self.respond_json(200, data)
            except Exception as e:
                self.respond_json(502, {'error': 'Failed to fetch data', 'detail': str(e)})
        else:
            self.respond_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.respond_json(400, {"error": "Empty payload"})
                return
            body = self.rfile.read(content_length)
            import json
            try:
                payload = json.loads(body)
            except Exception:
                self.respond_json(400, {"error": "Invalid JSON"})
                return
            try:
                result = self.device_client.send_command(payload)
                self.respond_json(200, result)
            except Exception as e:
                self.respond_json(502, {'error': 'Failed to send command', 'detail': str(e)})
        else:
            self.respond_json(404, {"error": "Not Found"})

    def respond_json(self, code, obj):
        import json
        data = json.dumps(obj).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        # Suppress default logging (optional – uncomment to enable logs)
        pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def main():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), IoTHTTPRequestHandler)
    print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()