import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver

# Mock device communication
# Since "dsad" protocol and device details are not specified, we'll simulate device communication.
# The "data" will be a static XML, and commands will be echoed back.

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Read configuration from environment variables
DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))  # Port to connect to device (simulated)
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

# Simulated XML data point
SIMULATED_XML_DATA = '''<?xml version="1.0" encoding="UTF-8"?>
<device>
    <data_point>42</data_point>
    <status>OK</status>
</device>
'''

# Simulated command response (echo)
def send_command_to_device(cmd_xml: str):
    # In real implementation, connect to device and send cmd_xml, receive response
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<response>
    <result>success</result>
    <echo>{cmd_xml}</echo>
</response>
'''

class DeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/xml"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            self._set_headers()
            # Simulate fetch from device using dsad protocol, return XML directly
            self.wfile.write(SIMULATED_XML_DATA.encode('utf-8'))
        elif self.path == '/info':
            self._set_headers(200, "application/json")
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                cmd_xml = post_data.decode('utf-8')
            except Exception:
                self._set_headers(400, "application/xml")
                self.wfile.write(b'<response><result>error</result><message>Invalid encoding</message></response>')
                return
            # Simulate sending command to device and getting XML response
            resp_xml = send_command_to_device(cmd_xml)
            self._set_headers(200, "application/xml")
            self.wfile.write(resp_xml.encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        # Suppress default logging
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), DeviceHTTPRequestHandler)
    print(f"Starting HTTP server on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    run_server()