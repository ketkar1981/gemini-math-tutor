const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const API_TARGET = process.env.API_TARGET || 'http://localhost:8000';

// Serve static frontend files from ./public
app.use(express.static(path.join(__dirname, 'public')));

// Proxy API requests to the backend server to avoid CORS and to keep the frontend simple.
// The frontend will call /api/generate which gets proxied to http://localhost:8000/generate
app.use('/api', createProxyMiddleware({
  target: API_TARGET,
  changeOrigin: true,
  pathRewrite: { '^/api': '' },
  logLevel: 'warn'
}));

app.listen(PORT, () => {
  console.log(`Frontend server running: http://localhost:${PORT}`);
  console.log(`Proxying /api -> ${API_TARGET}`);
});
