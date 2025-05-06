import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET
import threading

# Get configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Device static info as per requirements
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulated device TCP communication
def send_device_command(command_xml):
    """
    Connect to the device over TCP, send XML command, and receive XML response.
    """
    import socket
    with socket.create_connection((DEVICE_IP, DEVICE_PORT), timeout=5) as sock:
        if isinstance(command_xml, str):
            command_xml = command_xml.encode()
        sock.sendall(command_xml)
        # Read response with a simple buffer (for demo). Real device may vary.
        response = b""
        while True:
            part = sock.recv(4096)
            if not part:
                break
            response += part
            if b"</response>" in response or b"</data>" in response or b"</result>" in response:
                break
        return response

class IoTDeviceHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), 'utf-8'))
        elif self.path == '/data':
            try:
                # Example XML request to fetch data points/status
                xml_request = '''<request><action>get_data</action></request>'''
                xml_response = send_device_command(xml_request)
                # Convert XML to JSON-like dict (simple implementation)
                root = ET.fromstring(xml_response)
                data_dict = {child.tag: child.text for child in root}
                self._set_headers(200, "application/json")
                self.wfile.write(bytes(str(data_dict).replace("'", '"'), 'utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(bytes('{"error": "%s"}' % str(e), 'utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                # Accepts XML or JSON, but device expects XML, so convert if necessary
                if self.headers.get('Content-Type', '').startswith('application/json'):
                    import json
                    cmd_dict = json.loads(post_data.decode('utf-8'))
                    # Convert JSON to XML command (simple flat dict assumed)
                    xml_payload = "<request><action>command</action>"
                    for k, v in cmd_dict.items():
                        xml_payload += f"<{k}>{v}</{k}>"
                    xml_payload += "</request>"
                else:
                    # Assume raw XML
                    xml_payload = post_data
                xml_response = send_device_command(xml_payload)
                # Parse response XML for user-friendly output
                root = ET.fromstring(xml_response)
                resp_dict = {child.tag: child.text for child in root}
                self._set_headers(200, "application/json")
                self.wfile.write(bytes(str(resp_dict).replace("'", '"'), 'utf-8'))
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(bytes('{"error": "%s"}' % str(e), 'utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Not found"}')

    def log_message(self, format, *args):
        # Optional: Comment this method to enable default logging
        pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTDeviceHandler)
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()