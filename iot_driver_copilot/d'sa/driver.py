import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import xml.etree.ElementTree as ET

DEVICE_IP = os.environ.get('DEVICE_IP', '127.0.0.1')
DEVICE_PORT = int(os.environ.get('DEVICE_PORT', '9000'))
SERVER_HOST = os.environ.get('SERVER_HOST', '0.0.0.0')
SERVER_PORT = int(os.environ.get('SERVER_PORT', '8080'))

DEVICE_INFO = {
    "device_name": "d'sa",
    "device_model": "dsad'sa",
    "manufacturer": "dasdasdas",
    "device_type": "dsa"
}

class DeviceComm:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def fetch_data(self):
        try:
            with socket.create_connection((self.ip, self.port), timeout=5) as sock:
                req = "<request><action>get_data</action></request>"
                sock.sendall(req.encode('utf-8'))
                data = self._recv_all(sock)
                return data
        except Exception as e:
            return None

    def send_command(self, xml_command):
        try:
            with socket.create_connection((self.ip, self.port), timeout=5) as sock:
                sock.sendall(xml_command.encode('utf-8'))
                resp = self._recv_all(sock)
                return resp
        except Exception as e:
            return None

    def _recv_all(self, sock):
        sock.settimeout(2)
        chunks = []
        try:
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                chunks.append(data)
        except socket.timeout:
            pass
        return b''.join(chunks).decode('utf-8') if chunks else ''

class Handler(BaseHTTPRequestHandler):
    comm = DeviceComm(DEVICE_IP, DEVICE_PORT)

    def _set_headers(self, code=200, content_type="application/json"):
        self.send_response(code)
        self.send_header("Content-type", content_type)
        self.end_headers()

    def do_GET(self):
        if self.path == '/info':
            self._set_headers()
            self.wfile.write(bytes(str(DEVICE_INFO), 'utf-8'))
        elif self.path == '/data':
            data = self.comm.fetch_data()
            if not data:
                self._set_headers(502)
                self.wfile.write(b'{"error":"Failed to fetch device data"}')
                return
            # Try parse XML and convert to JSON-like dict
            try:
                root = ET.fromstring(data)
                resp = self._xml_to_dict(root)
            except Exception:
                resp = {"raw": data}
            self._set_headers()
            self.wfile.write(bytes(str(resp), 'utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Endpoint not found"}')

    def do_POST(self):
        if self.path == '/cmd':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8')
            # Expecting body as JSON with 'command'
            import json
            try:
                req = json.loads(body)
                command = req.get('command')
                if not command:
                    raise Exception()
            except Exception:
                self._set_headers(400)
                self.wfile.write(b'{"error":"Invalid request body"}')
                return
            # Convert command to XML
            xml_cmd = f"<request><action>command</action><cmd>{command}</cmd></request>"
            resp = self.comm.send_command(xml_cmd)
            if not resp:
                self._set_headers(502)
                self.wfile.write(b'{"error":"Device did not respond"}')
                return
            try:
                root = ET.fromstring(resp)
                resp_body = self._xml_to_dict(root)
            except Exception:
                resp_body = {"raw": resp}
            self._set_headers()
            self.wfile.write(bytes(str(resp_body), 'utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"Endpoint not found"}')

    def _xml_to_dict(self, root):
        d = {root.tag: {} if root.attrib else None}
        children = list(root)
        if children:
            dd = {}
            for dc in map(self._xml_to_dict, children):
                for k, v in dc.items():
                    if k in dd:
                        if not isinstance(dd[k], list):
                            dd[k] = [dd[k]]
                        dd[k].append(v)
                    else:
                        dd[k] = v
            d = {root.tag: dd}
        if root.attrib:
            d[root.tag].update(('@' + k, v) for k, v in root.attrib.items())
        if root.text:
            text = root.text.strip()
            if children or root.attrib:
                if text:
                    d[root.tag]['#text'] = text
            else:
                d[root.tag] = text
        return d

def run():
    server = HTTPServer((SERVER_HOST, SERVER_PORT), Handler)
    print(f"HTTP server running on {SERVER_HOST}:{SERVER_PORT}")
    server.serve_forever()

if __name__ == '__main__':
    run()
