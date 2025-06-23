const http = require('http');
const url = require('url');

// Configuration using environment variables
const SERVER_HOST = process.env.SERVER_HOST || '0.0.0.0';
const SERVER_PORT = parseInt(process.env.SERVER_PORT, 10) || 8080;

// Mock device data storage
let deviceData = [
  { id: 1, type: 'temperature', value: 23.5, timestamp: Date.now() },
  { id: 2, type: 'humidity', value: 50, timestamp: Date.now() },
  { id: 3, type: 'pressure', value: 1012, timestamp: Date.now() }
];

// Simulate command execution
function executeDeviceCommand(command) {
  // Here you would integrate with the real device logic
  if (!command || !command.cmd) return { success: false, message: 'No command specified.' };
  if (command.cmd === 'restart') {
    // Simulate restart
    return { success: true, message: 'Device restarted.' };
  }
  if (command.cmd === 'update') {
    // Simulate update
    return { success: true, message: 'Device updated.' };
  }
  return { success: false, message: 'Unknown command.' };
}

// Helper: Parse JSON body
function getJsonBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        resolve(JSON.parse(body));
      } catch (e) {
        reject(e);
      }
    });
  });
}

// HTTP Server
const server = http.createServer(async (req, res) => {
  const parsedUrl = url.parse(req.url, true);

  // GET /data
  if (req.method === 'GET' && parsedUrl.pathname === '/data') {
    // Filtering
    let data = deviceData;
    const { type, page, limit } = parsedUrl.query;
    if (type) {
      data = data.filter(d => d.type === type);
    }
    // Pagination
    let pageNum = parseInt(page, 10) || 1;
    let limitNum = parseInt(limit, 10) || data.length;
    let start = (pageNum - 1) * limitNum;
    let paginated = data.slice(start, start + limitNum);

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      data: paginated,
      total: data.length,
      page: pageNum,
      limit: limitNum
    }));
    return;
  }

  // POST /commands
  if (req.method === 'POST' && parsedUrl.pathname === '/commands') {
    if (req.headers['content-type'] !== 'application/json') {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Content-Type must be application/json' }));
      return;
    }
    try {
      const command = await getJsonBody(req);
      const result = executeDeviceCommand(command);
      if (result.success) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'success', message: result.message }));
      } else {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'failure', message: result.message }));
      }
    } catch (e) {
      res.writeHead(400, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'Invalid JSON body' }));
    }
    return;
  }

  // 404 for all other endpoints
  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'Not found' }));
});

// Start server
server.listen(SERVER_PORT, SERVER_HOST, () => {
  // No console.log as per requirements
});