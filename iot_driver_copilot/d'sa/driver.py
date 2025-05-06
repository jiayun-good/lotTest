import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
from urllib.parse import urlparse, parse_qs
import xml.etree.ElementTree as ET

# Configuration from environment variables
DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9001"))  # hypothetical dsad protocol port
SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

# Device static information
DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

# Simulated protocol handler (replace with real protocol handling)
def dsad_get_data(ip, port):
    # Simulate device response in XML
    # Normally here you would connect to the device using the dsad protocol
    # and retrieve the XML data stream, parse, and return it.
    # This is a stub for demonstration.
    xml_data = f"""
    <DeviceData>
        <DataPoint name="temperature" value="23.5" unit="C"/>
        <DataPoint name="humidity" value="56" unit="%"/>
        <Status value="OK"/>
    </DeviceData>
    """
    return xml_data.strip()

def dsad_send_command(ip, port, command_xml):
    # Simulate sending a command in XML and getting a response
    # Replace this stub with actual protocol logic.
    root = ET.fromstring(command_xml)
    # Simulate a successful command execution
    resp = f"""
    <CommandResponse>
        <Status>Success</Status>
        <Command>{root.tag}</Command>
    </CommandResponse>
    """
    return resp.strip()

# HTTP Server Implementation
class IoTDeviceHandler(BaseHTTPRequestHandler):

    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/info":
            self._set_headers(200, "application/json")
            self.wfile.write(bytes(str(DEVICE_INFO).replace("'", '"'), "utf-8"))
        elif parsed.path == "/data":
            # Proxy dsad protocol data into HTTP
            xml_data = dsad_get_data(DEVICE_IP, DEVICE_PORT)
            # Convert XML to JSON-like dict for HTTP, or return XML for browser consumption
            accept = self.headers.get("Accept", "")
            if "application/json" in accept:
                # Parse XML and convert to dict
                root = ET.fromstring(xml_data)
                result = {}
                for child in root:
                    if child.tag == "DataPoint":
                        if "data_points" not in result:
                            result["data_points"] = []
                        result["data_points"].append(child.attrib)
                    else:
                        result[child.tag] = child.attrib if child.attrib else child.text
                self._set_headers(200, "application/json")
                import json
                self.wfile.write(bytes(json.dumps(result), "utf-8"))
            else:
                self._set_headers(200, "application/xml")
                self.wfile.write(bytes(xml_data, "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/cmd":
            content_length = int(self.headers.get("Content-Length", 0))
            raw_post = self.rfile.read(content_length).decode("utf-8")
            # Expect XML payload
            try:
                ET.fromstring(raw_post)
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(b'{"error": "Invalid XML payload"}')
                return
            # Send command via dsad protocol
            resp_xml = dsad_send_command(DEVICE_IP, DEVICE_PORT, raw_post)
            accept = self.headers.get("Accept", "")
            if "application/json" in accept:
                # Convert XML to JSON
                root = ET.fromstring(resp_xml)
                result = {child.tag: child.text for child in root}
                import json
                self._set_headers(200, "application/json")
                self.wfile.write(bytes(json.dumps(result), "utf-8"))
            else:
                self._set_headers(200, "application/xml")
                self.wfile.write(bytes(resp_xml, "utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    server_address = (SERVER_HOST, SERVER_PORT)
    httpd = ThreadedHTTPServer(server_address, IoTDeviceHandler)
    print(f"HTTP server running at http://{SERVER_HOST}:{SERVER_PORT}/")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()