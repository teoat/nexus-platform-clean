/** * Development Proxy Configuration * Routes API requests to the backend server */ const {
  createProxyMiddleware,
} = require("http-proxy-middleware");
module.exports = function (app) {
  app.use(
    "/api",
    createProxyMiddleware({
      target: process.env.REACT_APP_API_URL || "http://localhost:8000",
      changeOrigin: true,
      secure: false,
      logLevel: "debug",
      onError: (err, req, res) => {
        console.error("Proxy error:", err);
        res.writeHead(500, { "Content-Type": "text/plain" });
        res.end("Proxy error: " + err.message);
      },
      onProxyReq: (proxyReq, req, res) => {
        console.log("Proxying request:", req.method, req.url);
      },
      onProxyRes: (proxyRes, req, res) => {
        console.log("Proxy response:", proxyRes.statusCode, req.url);
      },
    }),
  );
  app.use(
    "/health",
    createProxyMiddleware({
      target: process.env.REACT_APP_API_URL || "http://localhost:8000",
      changeOrigin: true,
      secure: false,
    }),
  );
};
