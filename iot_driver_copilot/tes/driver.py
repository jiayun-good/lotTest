import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import xml.etree.ElementTree as ET

DEVICE_INFO = {
    "device_name": "tes",
    "device_model": "tt",
    "manufacturer": "ttt",
    "device_type": "ttt"
}
CONNECTION_INFO = {
    "primary_protocol": "ttt"
}
KEY_CHARACTERISTICS = {
    "data_points": "tt",
    "commands": "ttt"
}
DATA_FORMAT = {
    "format": "XML"
}

def get_env(name, default=None, required=False):
    val = os.environ.get(name, default)
    if required and val is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return val

DEVICE_IP = get_env("DEVICE_IP", required=True)
DEVICE_PORT = int(get_env("DEVICE_PORT", 9000))
SERVER_HOST = get_env("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(get_env("SERVER_PORT", 8080))

def fake_device_request_xml(path, method="GET", payload=None):
    """
    Simulate a connection to a device over 'ttt' protocol,
    returning XML-formatted responses. Replace this with a
    real protocol implementation if available.
    """
    # All responses are XML
    if path == "/data" and method == "GET":
        root = ET.Element("DeviceData")
        ET.SubElement(root, "Temperature").text = "23.5"
        ET.SubElement(root, "Humidity").text = "41.2"
        return ET.tostring(root, encoding='utf-8', method='xml')
    elif path == "/test" and method == "POST":
        root = ET.Element("TestResult")
        ET.SubElement(root, "Status").text = "Success"
        ET.SubElement(root, "Message").text = "Device responded to test command."
        return ET.tostring(root, encoding='utf-8', method='xml')
    return None

class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            resp = {
                "device_info": DEVICE_INFO,
                "connection_info": CONNECTION_INFO,
                "key_characteristics": KEY_CHARACTERISTICS,
                "data_format": DATA_FORMAT
            }
            self.wfile.write(bytes(str(resp).replace("'", '"'), "utf-8"))
        elif self.path == "/data":
            xml_data = fake_device_request_xml("/data", "GET")
            if xml_data:
                self._set_headers(200, "application/xml")
                self.wfile.write(xml_data)
            else:
                self._set_headers(500)
                self.wfile.write(b"<error>Could not retrieve data</error>")
        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/test":
            content_length = int(self.headers.get('Content-Length', 0))
            _ = self.rfile.read(content_length) if content_length > 0 else None
            xml_data = fake_device_request_xml("/test", "POST")
            if xml_data:
                self._set_headers(200, "application/xml")
                self.wfile.write(xml_data)
            else:
                self._set_headers(500)
                self.wfile.write(b"<error>Test command failed</error>")
        else:
            self._set_headers(404)
            self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        # Silence the default HTTP server logging
        return

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    pass

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, Handler)
    print(f"Starting HTTP server at http://{SERVER_HOST}:{SERVER_PORT}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()