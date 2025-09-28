const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Backend API proxy
  app.use(
    '/api',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug',
      onError: (err, req, res) => {
        console.error('API Proxy Error:', err);
        res.status(500).json({ error: 'API Proxy Error' });
      }
    })
  );
  
  // Frenly AI proxy
  app.use(
    '/ai',
    createProxyMiddleware({
      target: 'http://localhost:8001',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug',
      ws: true, // Enable WebSocket support
      onError: (err, req, res) => {
        console.error('AI Proxy Error:', err);
        res.status(500).json({ error: 'AI Proxy Error' });
      }
    })
  );
  
  // Health check proxy
  app.use(
    '/health',
    createProxyMiddleware({
      target: 'http://localhost:8000',
      changeOrigin: true,
      secure: false,
      logLevel: 'debug'
    })
  );

  // WebSocket proxy for real-time features
  app.use(
    '/ws',
    createProxyMiddleware({
      target: 'ws://localhost:8000',
      ws: true,
      changeOrigin: true,
      logLevel: 'debug'
    })
  );
};
