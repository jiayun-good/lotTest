const http = require('http');
const url = require('url');

// Load configuration from environment variables
const SERVER_HOST = process.env.SERVER_HOST || '0.0.0.0';
const SERVER_PORT = parseInt(process.env.SERVER_PORT, 10) || 8080;

// Simulated device memory storage for data points and command results
let deviceData = [
    { id: 1, type: 'temperature', value: 22.5, timestamp: Date.now() - 60000 },
    { id: 2, type: 'humidity', value: 51.2, timestamp: Date.now() - 50000 },
    { id: 3, type: 'temperature', value: 23.1, timestamp: Date.now() - 40000 },
    { id: 4, type: 'pressure', value: 101.3, timestamp: Date.now() - 30000 },
    { id: 5, type: 'humidity', value: 52.0, timestamp: Date.now() - 20000 },
    { id: 6, type: 'temperature', value: 23.4, timestamp: Date.now() - 10000 },
    { id: 7, type: 'pressure', value: 101.2, timestamp: Date.now() },
];

function sendJSON(res, status, data) {
    res.writeHead(status, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(data));
}

// /data GET endpoint handler
function handleGetData(req, res) {
    const parsedUrl = url.parse(req.url, true);
    let { type, page, limit } = parsedUrl.query;

    let results = deviceData.slice();

    // Filtering
    if (type) {
        results = results.filter(d => d.type === type);
    }

    // Pagination
    page = parseInt(page, 10) || 1;
    limit = parseInt(limit, 10) || results.length;
    const start = (page - 1) * limit;
    const paginated = results.slice(start, start + limit);

    sendJSON(res, 200, {
        page,
        limit,
        total: results.length,
        data: paginated
    });
}

// /commands POST endpoint handler
function handlePostCommand(req, res) {
    let body = '';
    req.on('data', chunk => {
        body += chunk;
        if (body.length > 1e6) req.connection.destroy(); // Prevent DOS
    });
    req.on('end', () => {
        let payload;
        try {
            payload = JSON.parse(body);
        } catch (e) {
            sendJSON(res, 400, { error: 'Invalid JSON' });
            return;
        }
        // Dummy command processing
        if (!payload || !payload.command) {
            sendJSON(res, 400, { error: 'Missing command in payload' });
            return;
        }
        // Example: handle restart/update
        if (payload.command === 'restart' || payload.command === 'update') {
            sendJSON(res, 200, { status: 'success', message: `Command '${payload.command}' executed` });
        } else {
            sendJSON(res, 400, { status: 'error', message: `Unknown command '${payload.command}'` });
        }
    });
}

// HTTP server
const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);

    if (req.method === 'GET' && parsedUrl.pathname === '/data') {
        handleGetData(req, res);
    } else if (req.method === 'POST' && parsedUrl.pathname === '/commands') {
        handlePostCommand(req, res);
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Not found' }));
    }
});

server.listen(SERVER_PORT, SERVER_HOST, () => {
    // Server running
});