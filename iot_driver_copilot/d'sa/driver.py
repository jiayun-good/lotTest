import os
import threading
import http.server
import socketserver
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
import json

# Simulated device communication (since protocol is not standard)
class DSADDeviceClient:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def fetch_data(self):
        # Simulate device response in XML format
        # In real situation, replace with actual device communication logic
        xml_response = """<data_points>
            <temperature>23.5</temperature>
            <humidity>48</humidity>
            <status>OK</status>
        </data_points>"""
        return xml_response

    def send_command(self, command_xml):
        # Simulate command processing and response from device
        # In real situation, replace with actual sending logic
        # Here we "parse" the command and return a simulated response
        try:
            root = ET.fromstring(command_xml)
            cmd_name = root.tag
            response = f"<response><result>success</result><command>{cmd_name}</command></response>"
        except Exception as e:
            response = f"<response><result>error</result><message>{str(e)}</message></response>"
        return response

    def get_info(self):
        # Simulate device info
        return {
            "device_name": os.environ.get("DEVICE_NAME", "d'sa"),
            "device_model": os.environ.get("DEVICE_MODEL", "dsad'sa"),
            "manufacturer": os.environ.get("DEVICE_MANUFACTURER", "dasdasdas"),
            "device_type": os.environ.get("DEVICE_TYPE", "dsa")
        }

# HTTP Handler
class DSADHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    device_client = None

    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/data":
            xml_data = self.device_client.fetch_data()
            # Convert XML to JSON for HTTP response
            data_dict = self.xml_to_dict(xml_data)
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(data_dict).encode("utf-8"))
        elif parsed_path.path == "/info":
            info = self.device_client.get_info()
            self._set_headers(200, "application/json")
            self.wfile.write(json.dumps(info).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/cmd":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            # Assume XML payload
            try:
                command_xml = post_data.decode("utf-8")
                response_xml = self.device_client.send_command(command_xml)
                response_dict = self.xml_to_dict(response_xml)
                self._set_headers(200, "application/json")
                self.wfile.write(json.dumps(response_dict).encode("utf-8"))
            except Exception as e:
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error": "Not found"}')

    def xml_to_dict(self, xml_str):
        def _etree_to_dict(t):
            d = {t.tag: {} if t.attrib else None}
            children = list(t)
            if children:
                dd = {}
                for dc in map(_etree_to_dict, children):
                    for k, v in dc.items():
                        if k in dd:
                            if not isinstance(dd[k], list):
                                dd[k] = [dd[k]]
                            dd[k].append(v)
                        else:
                            dd[k] = v
                d = {t.tag: dd}
            if t.text:
                text = t.text.strip()
                if children or t.attrib:
                    if text:
                        d[t.tag]['text'] = text
                else:
                    d[t.tag] = text
            return d
        root = ET.fromstring(xml_str)
        return _etree_to_dict(root)

def run_server():
    DEVICE_IP = os.environ.get("DEVICE_IP", "127.0.0.1")
    DEVICE_PORT = int(os.environ.get("DEVICE_PORT", "9000"))

    SERVER_HOST = os.environ.get("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.environ.get("SERVER_PORT", "8080"))

    DSADHTTPRequestHandler.device_client = DSADDeviceClient(DEVICE_IP, DEVICE_PORT)

    with socketserver.ThreadingTCPServer((SERVER_HOST, SERVER_PORT), DSADHTTPRequestHandler) as httpd:
        print(f"Serving HTTP on {SERVER_HOST}:{SERVER_PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()