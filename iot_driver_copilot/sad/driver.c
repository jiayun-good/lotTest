#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <pthread.h>

#define MAX_REQ_SIZE 8192
#define MAX_RESP_SIZE 16384

typedef struct {
    char device_name[64];
    char device_model[64];
    char manufacturer[64];
    char device_type[64];
    char primary_protocol[32];
    char data_points[128];
    char commands[128];
    char data_format[16];
} DeviceInfo;

DeviceInfo device_info = {
    .device_name = "sad",
    .device_model = "asd",
    .manufacturer = "dsa",
    .device_type = "dsdsa",
    .primary_protocol = "das",
    .data_points = "s",
    .commands = "dasa",
    .data_format = "JSON"
};

char* get_env(const char* var, const char* def) {
    char* v = getenv(var);
    return v ? v : (char*)def;
}

void send_http_response(int client_fd, const char* status, const char* content_type, const char* body) {
    char response[MAX_RESP_SIZE];
    int len = snprintf(response, sizeof(response),
        "HTTP/1.1 %s\r\n"
        "Content-Type: %s\r\n"
        "Content-Length: %zu\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "Connection: close\r\n"
        "\r\n"
        "%s",
        status, content_type, strlen(body), body);
    send(client_fd, response, len, 0);
}

void send_http_json(int client_fd, const char* status, const char* json) {
    send_http_response(client_fd, status, "application/json", json);
}

void send_http_text(int client_fd, const char* status, const char* text) {
    send_http_response(client_fd, status, "text/plain", text);
}

void json_escape(const char* src, char* dest, size_t maxlen) {
    size_t j = 0;
    for (size_t i = 0; src[i] && j < maxlen - 1; ++i) {
        if (src[i] == '"' || src[i] == '\\') {
            if (j < maxlen - 2) {
                dest[j++] = '\\';
                dest[j++] = src[i];
            }
        } else if ((unsigned char)src[i] < 32) {
            if (j < maxlen - 7) {
                sprintf(dest + j, "\\u%04x", src[i]);
                j += 6;
            }
        } else {
            dest[j++] = src[i];
        }
    }
    dest[j] = 0;
}

// Simulated DAS protocol exchange (replace with actual implementation)
void simulate_das_query(char* outbuf, size_t maxlen) {
    snprintf(outbuf, maxlen, "{\"status\":\"ok\",\"data\":{\"point\":42}}");
}

// Simulated DAS command (replace with actual implementation)
void simulate_das_command(const char* cmd, char* outbuf, size_t maxlen) {
    snprintf(outbuf, maxlen, "{\"status\":\"command_received\",\"command\":\"%s\"}", cmd);
}

void handle_info(int client_fd) {
    char esc_name[128], esc_model[128], esc_manu[128], esc_type[128], esc_proto[64];
    json_escape(device_info.device_name, esc_name, sizeof(esc_name));
    json_escape(device_info.device_model, esc_model, sizeof(esc_model));
    json_escape(device_info.manufacturer, esc_manu, sizeof(esc_manu));
    json_escape(device_info.device_type, esc_type, sizeof(esc_type));
    json_escape(device_info.primary_protocol, esc_proto, sizeof(esc_proto));
    char json[1024];
    snprintf(json, sizeof(json),
        "{"
        "\"device_name\":\"%s\","
        "\"device_model\":\"%s\","
        "\"manufacturer\":\"%s\","
        "\"device_type\":\"%s\","
        "\"primary_protocol\":\"%s\""
        "}",
        esc_name, esc_model, esc_manu, esc_type, esc_proto
    );
    send_http_json(client_fd, "200 OK", json);
}

void handle_cmd(int client_fd, const char* body) {
    char cmd_json[512];
    // Find "command" in body (naive JSON parse)
    const char* cmd_start = strstr(body, "\"command\"");
    if (cmd_start) {
        const char* quote1 = strchr(cmd_start, ':');
        if (quote1) {
            quote1++;
            while (*quote1 == ' ' || *quote1 == '"') quote1++;
            const char* quote2 = strchr(quote1, '"');
            if (quote2) {
                size_t cmd_len = quote2 - quote1;
                char cmd[128] = {0};
                strncpy(cmd, quote1, cmd_len > 127 ? 127 : cmd_len);
                simulate_das_command(cmd, cmd_json, sizeof(cmd_json));
                send_http_json(client_fd, "200 OK", cmd_json);
                return;
            }
        }
    }
    send_http_json(client_fd, "400 Bad Request", "{\"error\":\"Invalid command payload\"}");
}

void handle_not_found(int client_fd) {
    send_http_json(client_fd, "404 Not Found", "{\"error\":\"Not found\"}");
}

void handle_req(int client_fd, const char* req, ssize_t req_len) {
    char method[8], path[64];
    sscanf(req, "%7s %63s", method, path);

    if (strcmp(method, "GET") == 0 && strcmp(path, "/info") == 0) {
        handle_info(client_fd);
    } else if (strcmp(method, "POST") == 0 && strcmp(path, "/cmd") == 0) {
        // Find body
        const char* body = strstr(req, "\r\n\r\n");
        if (body) body += 4;
        else body = "";
        handle_cmd(client_fd, body);
    } else {
        handle_not_found(client_fd);
    }
}

void* client_thread(void* arg) {
    int client_fd = *(int*)arg;
    free(arg);
    char req[MAX_REQ_SIZE];
    ssize_t r = recv(client_fd, req, sizeof(req)-1, 0);
    if (r > 0) {
        req[r] = 0;
        handle_req(client_fd, req, r);
    }
    close(client_fd);
    return NULL;
}

int main() {
    const char* SERVER_HOST = get_env("SERVER_HOST", "0.0.0.0");
    int SERVER_PORT = atoi(get_env("SERVER_PORT", "8080"));
    int das_port = atoi(get_env("DAS_PORT", "12345"));
    const char* das_ip = get_env("DAS_IP", "127.0.0.1");

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket()");
        exit(1);
    }

    int optval = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &optval, sizeof(optval));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(SERVER_PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    if (strcmp(SERVER_HOST, "0.0.0.0") != 0) {
        addr.sin_addr.s_addr = inet_addr(SERVER_HOST);
    }

    if (bind(server_fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind()");
        exit(1);
    }
    if (listen(server_fd, 16) < 0) {
        perror("listen()");
        exit(1);
    }

    printf("HTTP server running at %s:%d\n", SERVER_HOST, SERVER_PORT);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t ca_len = sizeof(client_addr);
        int* client_fd = malloc(sizeof(int));
        *client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &ca_len);
        if (*client_fd < 0) {
            free(client_fd);
            continue;
        }
        pthread_t tid;
        pthread_create(&tid, NULL, client_thread, client_fd);
        pthread_detach(tid);
    }
    close(server_fd);
    return 0;
}