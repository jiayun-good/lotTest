import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading
import xml.etree.ElementTree as ET

# --- Device and Protocol Simulation (since 'dsad' protocol is unknown) ---

def get_device_data_points():
    # Simulate fetching data from the device using the 'dsad' protocol
    # Example XML data
    root = ET.Element("datapoints")
    ET.SubElement(root, "temperature").text = "25.3"
    ET.SubElement(root, "humidity").text = "60"
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)

def send_device_command(command_xml):
    # Simulate sending a command to the device and getting a response
    # Accepts XML and returns status as XML
    try:
        root = ET.fromstring(command_xml)
        response = ET.Element("command_response")
        ET.SubElement(response, "status").text = "success"
        ET.SubElement(response, "echo").append(root)
        return ET.tostring(response, encoding="utf-8", xml_declaration=True)
    except ET.ParseError:
        response = ET.Element("command_response")
        ET.SubElement(response, "status").text = "error"
        ET.SubElement(response, "error").text = "Malformed XML"
        return ET.tostring(response, encoding="utf-8", xml_declaration=True)

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# --- HTTP Server Implementation ---

class IoTDeviceHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/data':
            self._set_headers()
            data_xml = get_device_data_points()
            self.wfile.write(data_xml)
        elif self.path == '/info':
            self._set_headers(content_type="application/json")
            import json
            self.wfile.write(json.dumps(DEVICE_INFO).encode('utf-8'))
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b'Not Found')

    def do_POST(self):
        if self.path == '/cmd':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            response_xml = send_device_command(post_data)
            self._set_headers()
            self.wfile.write(response_xml)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b'Not Found')

    def log_message(self, format, *args):
        # Suppress default logging
        return

def run_server():
    server_host = os.environ.get('SERVER_HOST', '0.0.0.0')
    server_port = int(os.environ.get('SERVER_PORT', '8080'))
    with socketserver.ThreadingTCPServer((server_host, server_port), IoTDeviceHTTPRequestHandler) as httpd:
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()