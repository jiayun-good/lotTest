#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>

#define BUF_SIZE 8192
#define SMALL_BUF 256

// Device info statics for /info endpoint
const char *DEVICE_INFO_JSON =
    "{"
    "\"device_name\":\"sad\","
    "\"device_model\":\"asd\","
    "\"manufacturer\":\"dsa\","
    "\"device_type\":\"dsdsa\","
    "\"primary_protocol\":\"das\""
    "}";

// Command processing stub for /cmd endpoint
int handle_command(const char *json_payload, char *response, size_t maxlen) {
    // Simulate processing. In real world, send the command to the device.
    snprintf(response, maxlen, "{\"status\":\"success\",\"received\":%s}", json_payload);
    return 0;
}

// Helper: Read a line (request header or request line)
int read_line(int sock, char *buf, int size) {
    int i = 0, n;
    char c = '\0';
    while ((i < size - 1) && (c != '\n')) {
        n = read(sock, &c, 1);
        if (n > 0) {
            if (c == '\r') {
                // Peek next char, if '\n', consume it
                n = read(sock, &c, 1);
                if ((n > 0) && (c != '\n'))
                    buf[i++] = '\r';
                else
                    break;
            }
            buf[i++] = c;
        } else {
            c = '\n';
        }
    }
    buf[i] = '\0';
    return i;
}

// Helper: Parse Content-Length from headers
int get_content_length(const char *headers) {
    const char *p = strstr(headers, "Content-Length:");
    if (p) {
        p += strlen("Content-Length:");
        while (*p && isspace((unsigned char)*p)) p++;
        return atoi(p);
    }
    return 0;
}

// Helper: Get request path and method
void parse_request_line(const char *req_line, char *method, size_t mlen, char *path, size_t plen) {
    sscanf(req_line, "%s %s", method, path);
}

void send_http_response(int client, int code, const char *content_type, const char *body) {
    char header[SMALL_BUF];
    int body_len = strlen(body);
    snprintf(header, sizeof(header),
        "HTTP/1.1 %d %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %d\r\n"
        "Connection: close\r\n"
        "\r\n",
        code, (code == 200) ? "OK" : (code == 404) ? "Not Found" : "Error",
        content_type, body_len);
    write(client, header, strlen(header));
    write(client, body, body_len);
}

void handle_info(int client) {
    send_http_response(client, 200, "application/json", DEVICE_INFO_JSON);
}

void handle_cmd(int client, const char *headers, int content_length) {
    if (content_length > 2048) content_length = 2048;
    char *payload = (char *)malloc(content_length + 1);
    int total_read = 0, n;
    while (total_read < content_length) {
        n = read(client, payload + total_read, content_length - total_read);
        if (n <= 0) break;
        total_read += n;
    }
    payload[total_read] = '\0';

    char resp[2048];
    handle_command(payload, resp, sizeof(resp));
    free(payload);

    send_http_response(client, 200, "application/json", resp);
}

void not_found(int client) {
    send_http_response(client, 404, "text/plain", "Not Found");
}

void serve_forever(int server_port) {
    int server_fd, client_fd;
    struct sockaddr_in addr;
    socklen_t sin_len = sizeof(addr);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(server_port);

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        exit(1);
    }
    if (listen(server_fd, 10) < 0) {
        perror("listen");
        exit(1);
    }

    while (1) {
        client_fd = accept(server_fd, (struct sockaddr*)&addr, &sin_len);
        if (client_fd < 0) continue;

        char req_line[SMALL_BUF], method[SMALL_BUF], path[SMALL_BUF], headers[BUF_SIZE] = {0};
        int content_length = 0;

        // Read request line
        read_line(client_fd, req_line, sizeof(req_line));
        parse_request_line(req_line, method, sizeof(method), path, sizeof(path));

        // Read headers
        char line[SMALL_BUF];
        int header_len = 0;
        while (read_line(client_fd, line, sizeof(line)) > 2) {
            strncat(headers, line, sizeof(headers) - strlen(headers) - 1);
            header_len += strlen(line);
            if (header_len > BUF_SIZE - 128) break;
        }
        content_length = get_content_length(headers);

        // Dispatch
        if (strcmp(path, "/info") == 0 && strcmp(method, "GET") == 0) {
            handle_info(client_fd);
        } else if (strcmp(path, "/cmd") == 0 && strcmp(method, "POST") == 0) {
            handle_cmd(client_fd, headers, content_length);
        } else {
            not_found(client_fd);
        }

        close(client_fd);
    }
}

int main() {
    // Config via env
    char *env_port = getenv("HTTP_SERVER_PORT");
    int port = env_port ? atoi(env_port) : 8080;

    serve_forever(port);
    return 0;
}
