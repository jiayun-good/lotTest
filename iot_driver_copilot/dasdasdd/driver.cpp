#include <iostream>
#include <cstdlib>
#include <string>
#include <sstream>
#include <vector>
#include <map>
#include <cstring>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <netinet/in.h>
#include <unistd.h>

// --- Device Protocol Simulation (XML over TCP) ---
class DeviceConnection {
    std::string ip;
    int port;
public:
    DeviceConnection(const std::string& ip_, int port_) : ip(ip_), port(port_) {}
    // Simulate getting data points in XML
    std::string getDataPoints() {
        // Simulated device XML (replace with real protocol)
        return "<data><temperature>23</temperature><humidity>45</humidity></data>";
    }
    // Simulate sending a command and getting a response
    std::string sendCommand(const std::string& cmd) {
        // Simulated XML response
        return "<response><status>success</status><cmd>" + cmd + "</cmd></response>";
    }
    // Simulate device info in XML
    std::string getInfo() {
        return "<info>"
               "<device_name>dasdasdd</device_name>"
               "<device_model>asdasdad</device_model>"
               "<manufacturer>dsadasd</manufacturer>"
               "<device_type>asdasdad</device_type>"
               "<primary_protocol>dsada</primary_protocol>"
               "</info>";
    }
};

// --- HTTP Server Implementation (Basic) ---
class HTTPServer {
    int server_fd;
    std::string host;
    int port;
    DeviceConnection device;

    static std::map<std::string, std::string> parse_headers(const std::string& header_str) {
        std::map<std::string, std::string> headers;
        std::istringstream stream(header_str);
        std::string line;
        while (std::getline(stream, line) && line != "\r") {
            auto colon = line.find(':');
            if (colon != std::string::npos) {
                std::string key = line.substr(0, colon);
                std::string value = line.substr(colon + 1);
                while (!value.empty() && (value[0] == ' ' || value[0] == '\t')) value.erase(0,1);
                if (!value.empty() && value.back() == '\r') value.pop_back();
                headers[key] = value;
            }
        }
        return headers;
    }

    static void send_response(int client, const std::string& status, const std::string& content_type, const std::string& body) {
        std::ostringstream oss;
        oss << "HTTP/1.1 " << status << "\r\n"
            << "Content-Type: " << content_type << "\r\n"
            << "Content-Length: " << body.size() << "\r\n"
            << "Access-Control-Allow-Origin: *\r\n"
            << "Connection: close\r\n\r\n"
            << body;
        std::string resp = oss.str();
        send(client, resp.c_str(), resp.size(), 0);
    }

    void handle_client(int client_sock) {
        char buffer[4096];
        ssize_t bytes = recv(client_sock, buffer, sizeof(buffer) - 1, 0);
        if (bytes <= 0) {
            close(client_sock);
            return;
        }
        buffer[bytes] = '\0';
        std::string request(buffer);
        std::string method, path;
        std::istringstream req_stream(request);
        req_stream >> method >> path;
        // Parse headers and body
        size_t header_end = request.find("\r\n\r\n");
        std::string header_str = request.substr(0, header_end);
        std::map<std::string, std::string> headers = parse_headers(header_str);
        std::string body;
        if (header_end != std::string::npos) {
            body = request.substr(header_end + 4);
        }

        if (method == "GET" && path == "/data") {
            std::string xml = device.getDataPoints();
            send_response(client_sock, "200 OK", "application/xml", xml);
        } else if (method == "POST" && path == "/cmd") {
            // Parse command from body (assume body is plain text or XML)
            std::string cmd = body;
            std::string resp_xml = device.sendCommand(cmd);
            send_response(client_sock, "200 OK", "application/xml", resp_xml);
        } else if (method == "GET" && path == "/info") {
            std::string xml = device.getInfo();
            send_response(client_sock, "200 OK", "application/xml", xml);
        } else {
            send_response(client_sock, "404 Not Found", "text/plain", "404 Not Found");
        }
        close(client_sock);
    }
public:
    HTTPServer(const std::string& host_, int port_, const DeviceConnection& dev)
        : host(host_), port(port_), device(dev) {}

    void start() {
        server_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (server_fd == -1) {
            std::cerr << "Error: Cannot create socket\n";
            exit(1);
        }
        int opt = 1;
        setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in server_addr;
        server_addr.sin_family = AF_INET;
        server_addr.sin_port = htons(port);
        server_addr.sin_addr.s_addr = INADDR_ANY;

        if (bind(server_fd, (sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
            std::cerr << "Error: Cannot bind socket\n";
            exit(1);
        }
        if (listen(server_fd, 10) < 0) {
            std::cerr << "Error: Cannot listen\n";
            exit(1);
        }
        std::cout << "HTTP Server running on port " << port << std::endl;

        while (true) {
            sockaddr_in client_addr;
            socklen_t client_len = sizeof(client_addr);
            int client_sock = accept(server_fd, (sockaddr*)&client_addr, &client_len);
            if (client_sock < 0) continue;
            std::thread(&HTTPServer::handle_client, this, client_sock).detach();
        }
    }
};

// --- Main Entrypoint ---
int main() {
    // Configuration from environment variables
    std::string device_ip = std::getenv("DEVICE_IP") ? std::getenv("DEVICE_IP") : "127.0.0.1";
    int device_port = std::getenv("DEVICE_PORT") ? std::stoi(std::getenv("DEVICE_PORT")) : 9000;
    std::string server_host = std::getenv("SERVER_HOST") ? std::getenv("SERVER_HOST") : "0.0.0.0";
    int server_port = std::getenv("SERVER_PORT") ? std::stoi(std::getenv("SERVER_PORT")) : 8080;

    DeviceConnection dev(device_ip, device_port);
    HTTPServer server(server_host, server_port, dev);
    server.start();
    return 0;
}