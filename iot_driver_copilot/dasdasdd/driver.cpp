#include <iostream>
#include <sstream>
#include <cstdlib>
#include <cstring>
#include <string>
#include <map>
#include <vector>
#include <mutex>
#include <thread>
#include <algorithm>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>

// Simple HTTP server for device driver in C++
// All device configuration via environment variables

// Utility functions
std::string getenv_or_default(const char* key, const char* def) {
    const char* val = getenv(key);
    return val ? std::string(val) : std::string(def);
}

std::string url_decode(const std::string &src) {
    std::string ret;
    char ch;
    int i, ii;
    for (i=0; i<src.length(); i++) {
        if (int(src[i])==37) {
            sscanf(src.substr(i+1,2).c_str(), "%x", &ii);
            ch=static_cast<char>(ii);
            ret+=ch;
            i=i+2;
        } else {
            ret+=src[i];
        }
    }
    return ret;
}

struct DeviceInfo {
    std::string name, model, manufacturer, type, protocol;
};

struct HTTPRequest {
    std::string method;
    std::string path;
    std::map<std::string, std::string> headers;
    std::string body;
};

DeviceInfo getDeviceInfo() {
    DeviceInfo info;
    info.name = getenv_or_default("DEVICE_NAME", "dasdasdd");
    info.model = getenv_or_default("DEVICE_MODEL", "asdasdad");
    info.manufacturer = getenv_or_default("DEVICE_MANUFACTURER", "dsadasd");
    info.type = getenv_or_default("DEVICE_TYPE", "asdasdad");
    info.protocol = getenv_or_default("DEVICE_PROTOCOL", "dsada");
    return info;
}

// Simulate device XML data retrieval
std::string get_device_data_points_xml() {
    // In real implementation, replace with actual device communication
    std::string xml = 
        "<DeviceData>"
        "<DataPoint name=\"sadsa\">Value</DataPoint>"
        "<Status>OK</Status>"
        "</DeviceData>";
    return xml;
}

// Simulate sending command to device, and returning XML result
std::string process_device_command(const std::string& command) {
    // In real implementation, send command to device and return its response
    std::string xml = 
        "<CommandResponse>"
        "<Command>" + command + "</Command>"
        "<Result>Success</Result>"
        "</CommandResponse>";
    return xml;
}

std::string get_device_info_xml(const DeviceInfo& info) {
    std::ostringstream oss;
    oss << "<DeviceInfo>"
        << "<Name>" << info.name << "</Name>"
        << "<Model>" << info.model << "</Model>"
        << "<Manufacturer>" << info.manufacturer << "</Manufacturer>"
        << "<Type>" << info.type << "</Type>"
        << "<Protocol>" << info.protocol << "</Protocol>"
        << "</DeviceInfo>";
    return oss.str();
}

// HTTP helpers

void send_http_response(int client_sock, int code, const std::string& content_type, const std::string& body) {
    std::ostringstream oss;
    oss << "HTTP/1.1 " << code << " "
        << (code == 200 ? "OK" : "ERROR") << "\r\n"
        << "Content-Type: " << content_type << "\r\n"
        << "Content-Length: " << body.length() << "\r\n"
        << "Access-Control-Allow-Origin: *\r\n"
        << "\r\n"
        << body;
    std::string resp = oss.str();
    send(client_sock, resp.c_str(), resp.length(), 0);
}

void send_http_404(int client_sock) {
    send_http_response(client_sock, 404, "text/plain", "404 Not Found");
}

void send_http_405(int client_sock) {
    send_http_response(client_sock, 405, "text/plain", "405 Method Not Allowed");
}

// Simple HTTP request parser
bool parse_http_request(const std::string& req, HTTPRequest& out_req) {
    std::istringstream iss(req);
    std::string line;
    if (!std::getline(iss, line)) return false;
    std::istringstream liness(line);
    if (!(liness >> out_req.method >> out_req.path)) return false;
    std::string key, val;
    while (std::getline(iss, line) && line != "\r") {
        auto colon = line.find(':');
        if (colon != std::string::npos) {
            key = line.substr(0, colon);
            val = line.substr(colon+1);
            val.erase(0, val.find_first_not_of(" \t\r\n"));
            val.erase(val.find_last_not_of("\r\n")+1);
            out_req.headers[key] = val;
        }
    }
    if (out_req.headers.count("Content-Length")) {
        int len = std::stoi(out_req.headers["Content-Length"]);
        if (len > 0) {
            std::vector<char> buf(len);
            iss.read(buf.data(), len);
            out_req.body.assign(buf.data(), len);
        }
    }
    return true;
}

// Handler for each client
void handle_client(int client_sock, DeviceInfo device_info) {
    char buffer[8192];
    int recv_len = recv(client_sock, buffer, sizeof(buffer)-1, 0);
    if (recv_len <= 0) {
        close(client_sock);
        return;
    }
    buffer[recv_len] = 0;
    HTTPRequest req;
    if (!parse_http_request(buffer, req)) {
        send_http_response(client_sock, 400, "text/plain", "Bad Request");
        close(client_sock);
        return;
    }
    // Routing
    if (req.method == "GET" && req.path == "/data") {
        std::string xml = get_device_data_points_xml();
        send_http_response(client_sock, 200, "application/xml", xml);
    } else if (req.method == "POST" && req.path == "/cmd") {
        // Accept XML or text commands in body
        std::string command = req.body;
        std::string xml = process_device_command(command);
        send_http_response(client_sock, 200, "application/xml", xml);
    } else if (req.method == "GET" && req.path == "/info") {
        std::string xml = get_device_info_xml(device_info);
        send_http_response(client_sock, 200, "application/xml", xml);
    } else {
        send_http_404(client_sock);
    }
    close(client_sock);
}

int main() {
    // Read config from env
    std::string server_host = getenv_or_default("SERVER_HOST", "0.0.0.0");
    int server_port = std::stoi(getenv_or_default("SERVER_PORT", "8080"));
    DeviceInfo device_info = getDeviceInfo();

    int server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (server_sock < 0) {
        std::cerr << "Socket creation failed\n";
        return 1;
    }
    int opt = 1;
    setsockopt(server_sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr;
    addr.sin_family = AF_INET;
    addr.sin_port = htons(server_port);
    addr.sin_addr.s_addr = inet_addr(server_host.c_str());

    if (bind(server_sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "Bind failed\n";
        close(server_sock);
        return 1;
    }

    if (listen(server_sock, 10) < 0) {
        std::cerr << "Listen failed\n";
        close(server_sock);
        return 1;
    }

    std::cout << "Device HTTP server started on " << server_host << ":" << server_port << std::endl;

    while (true) {
        sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_sock = accept(server_sock, (struct sockaddr*)&client_addr, &client_len);
        if (client_sock < 0) continue;
        std::thread th(handle_client, client_sock, device_info);
        th.detach();
    }

    close(server_sock);
    return 0;
}