import os
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import threading

# --- Device Connection/Simulation ---

class DeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def get_data_points(self):
        # Simulate device data fetch, return XML string
        # In a real implementation, connect via socket and receive XML data.
        # Here, we mock XML data
        root = ET.Element("DeviceData")
        dp = ET.SubElement(root, "DataPoint")
        dp.set("name", "temperature")
        dp.text = "23.5"
        dp2 = ET.SubElement(root, "DataPoint")
        dp2.set("name", "humidity")
        dp2.text = "56"
        return ET.tostring(root, encoding="utf-8", method="xml")

    def send_command(self, command_xml):
        # Simulate sending command to device, return response XML
        # In a real implementation, connect via socket and send/receive.
        root = ET.Element("CommandResponse")
        root.text = "ok"
        return ET.tostring(root, encoding="utf-8", method="xml")

# --- HTTP Handler ---

class DriverHTTPRequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type="application/xml"):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == "/info":
            self._set_headers(200, "application/json")
            info = {
                "device_name": os.environ.get("DEVICE_NAME", ""),
                "device_model": os.environ.get("DEVICE_MODEL", ""),
                "manufacturer": os.environ.get("DEVICE_MANUFACTURER", ""),
                "device_type": os.environ.get("DEVICE_TYPE", ""),
            }
            self.wfile.write(bytes(str(info).replace("'", '"'), "utf-8"))
        elif self.path == "/data":
            self._set_headers(200, "application/xml")
            xml_data = self.server.device_client.get_data_points()
            self.wfile.write(xml_data)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Expecting XML payload
            try:
                ET.fromstring(post_data)
            except ET.ParseError:
                self._set_headers(400, "application/xml")
                self.wfile.write(b"<Error>Malformed XML</Error>")
                return
            resp_xml = self.server.device_client.send_command(post_data)
            self._set_headers(200, "application/xml")
            self.wfile.write(resp_xml)
        else:
            self._set_headers(404, "text/plain")
            self.wfile.write(b"Not Found")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True
    def __init__(self, server_address, RequestHandlerClass, device_client):
        super().__init__(server_address, RequestHandlerClass)
        self.device_client = device_client

def run():
    # Environment config
    DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
    DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "12345"))
    HTTP_HOST = os.environ.get("HTTP_HOST", "0.0.0.0")
    HTTP_PORT = int(os.environ.get("HTTP_PORT", "8080"))

    # Device meta for /info endpoint
    os.environ.setdefault("DEVICE_NAME", "d'sa")
    os.environ.setdefault("DEVICE_MODEL", "dsad'sa")
    os.environ.setdefault("DEVICE_MANUFACTURER", "dasdasdas")
    os.environ.setdefault("DEVICE_TYPE", "dsa")

    device_client = DeviceClient(DEVICE_IP, DEVICE_PORT)
    server = ThreadedHTTPServer((HTTP_HOST, HTTP_PORT), DriverHTTPRequestHandler, device_client)
    print(f"HTTP server running at http://{HTTP_HOST}:{HTTP_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    run()