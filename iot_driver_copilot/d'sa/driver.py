import os
import threading
import http.server
import socketserver
from http import HTTPStatus
import xml.etree.ElementTree as ET

DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

def fetch_device_data():
    # Simulate fetching XML data from the device using custom protocol "dsad"
    # Replace with actual device communication if available
    # Here we just create a sample XML for demonstration
    xml_data = f"""<?xml version="1.0"?>
<device>
    <data_points>
        <point name="dsa" value="123"/>
    </data_points>
    <status>OK</status>
</device>"""
    return xml_data

def send_device_command(command_xml):
    # Simulate sending command in XML format to the device using "dsad" protocol
    # Replace with actual device communication if available
    # Here we just echo back the command with a status
    try:
        ET.fromstring(command_xml)
        response = """<?xml version="1.0"?><response><status>success</status></response>"""
    except ET.ParseError:
        response = """<?xml version="1.0"?><response><status>invalid_xml</status></response>"""
    return response

class IoTDeviceHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status=HTTPStatus.OK, content_type="application/xml"):
        self.send_response(status)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(HTTPStatus.OK, "application/json")
            info_json = (
                '{'
                f'"device_name": {repr(DEVICE_INFO["device_name"])}, '
                f'"device_model": {repr(DEVICE_INFO["device_model"])}, '
                f'"manufacturer": {repr(DEVICE_INFO["manufacturer"])}, '
                f'"device_type": {repr(DEVICE_INFO["device_type"])}'
                '}'
            )
            self.wfile.write(info_json.encode())
        elif self.path == "/data":
            self._set_headers(HTTPStatus.OK, "application/xml")
            xml_data = fetch_device_data()
            self.wfile.write(xml_data.encode())
        else:
            self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
            self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length > 0 else b""
            command_xml = post_data.decode()
            response_xml = send_device_command(command_xml)
            self._set_headers(HTTPStatus.OK, "application/xml")
            self.wfile.write(response_xml.encode())
        else:
            self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
            self.wfile.write(b"Not found")

    def log_message(self, format, *args):
        # Suppress default logging
        pass

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

def run_server():
    server = ThreadedHTTPServer((SERVER_HOST, SERVER_PORT), IoTDeviceHandler)
    print(f"HTTP server started on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()