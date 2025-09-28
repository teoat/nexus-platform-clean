#!/usr/bin/env python3
"""
NEXUS Platform - API Gateway
Centralized API gateway with routing, middleware, and load balancing
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid
import hashlib
import hmac
import base64
from urllib.parse import urlparse, parse_qs
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
import jwt
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HTTPMethod(Enum):
    """HTTP method enumeration"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class RouteType(Enum):
    """Route type enumeration"""
    PROXY = "proxy"
    REDIRECT = "redirect"
    STATIC = "static"
    FUNCTION = "function"

@dataclass
class Route:
    """Route definition"""
    path: str
    method: HTTPMethod
    route_type: RouteType
    target_service: Optional[str] = None
    target_url: Optional[str] = None
    handler: Optional[Callable] = None
    middleware: List[str] = field(default_factory=list)
    rate_limit: Optional[int] = None  # requests per minute
    timeout: int = 30  # seconds
    retry_count: int = 3
    circuit_breaker: bool = True
    cache_ttl: int = 0  # seconds, 0 = no cache
    auth_required: bool = True
    roles: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MiddlewareConfig:
    """Middleware configuration"""
    name: str
    enabled: bool = True
    config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RateLimitInfo:
    """Rate limiting information"""
    key: str
    limit: int
    window: int  # seconds
    current_count: int = 0
    window_start: datetime = field(default_factory=datetime.now)
    blocked_until: Optional[datetime] = None

class CircuitBreaker:
    """Circuit breaker for service calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful execution"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed execution"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

class RateLimiter:
    """Rate limiting implementation"""
    
    def __init__(self):
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.cleanup_interval = 300  # 5 minutes
        self.cleanup_task = None
    
    async def start(self):
        """Start rate limiter cleanup task"""
        self.cleanup_task = asyncio.create_task(self._cleanup_expired_limits())
    
    async def stop(self):
        """Stop rate limiter cleanup task"""
        if self.cleanup_task:
            self.cleanup_task.cancel()
    
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """Check if request is allowed based on rate limit"""
        current_time = datetime.now()
        
        if key not in self.rate_limits:
            self.rate_limits[key] = RateLimitInfo(
                key=key,
                limit=limit,
                window=window
            )
        
        rate_info = self.rate_limits[key]
        
        # Check if currently blocked
        if rate_info.blocked_until and current_time < rate_info.blocked_until:
            return False
        
        # Reset window if needed
        if (current_time - rate_info.window_start).total_seconds() > window:
            rate_info.current_count = 0
            rate_info.window_start = current_time
            rate_info.blocked_until = None
        
        # Check limit
        if rate_info.current_count >= limit:
            rate_info.blocked_until = current_time + timedelta(seconds=window)
            return False
        
        # Increment counter
        rate_info.current_count += 1
        return True
    
    async def _cleanup_expired_limits(self):
        """Cleanup expired rate limits"""
        while True:
            try:
                current_time = datetime.now()
                expired_keys = []
                
                for key, rate_info in self.rate_limits.items():
                    if (current_time - rate_info.window_start).total_seconds() > rate_info.window * 2:
                        expired_keys.append(key)
                
                for key in expired_keys:
                    del self.rate_limits[key]
                
                await asyncio.sleep(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"Error in rate limiter cleanup: {e}")
                await asyncio.sleep(60)

class Cache:
    """Simple in-memory cache"""
    
    def __init__(self, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.access_times: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            self.access_times[key] = datetime.now()
            return self.cache[key]['value']
        return None
    
    def set(self, key: str, value: Any, ttl: int = 0):
        """Set value in cache"""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl) if ttl > 0 else None
        }
        self.access_times[key] = datetime.now()
    
    def delete(self, key: str):
        """Delete value from cache"""
        self.cache.pop(key, None)
        self.access_times.pop(key, None)
    
    def _evict_oldest(self):
        """Evict oldest accessed item"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.delete(oldest_key)
    
    def cleanup_expired(self):
        """Remove expired items"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, data in self.cache.items():
            if data['expires_at'] and current_time > data['expires_at']:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)

class APIGateway:
    """Main API Gateway class"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8000):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.routes: Dict[str, Route] = {}
        self.middleware: Dict[str, MiddlewareConfig] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.rate_limiter = RateLimiter()
        self.cache = Cache()
        self.session: Optional[ClientSession] = None
        from backend.config.settings import get_settings
        settings = get_settings()
        self.jwt_secret = settings.secret_key
        
        # Setup routes
        self._setup_routes()
        self._setup_middleware()
    
    async def start(self):
        """Start the API Gateway"""
        logger.info("Starting API Gateway...")
        
        # Start rate limiter
        await self.rate_limiter.start()
        
        # Create HTTP session
        timeout = ClientTimeout(total=30)
        self.session = ClientSession(timeout=timeout)
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        logger.info(f"API Gateway started on {self.host}:{self.port}")
    
    async def stop(self):
        """Stop the API Gateway"""
        logger.info("Stopping API Gateway...")
        
        # Stop rate limiter
        await self.rate_limiter.stop()
        
        # Close HTTP session
        if self.session:
            await self.session.close()
        
        logger.info("API Gateway stopped")
    
    def add_route(self, route: Route):
        """Add a new route"""
        route_key = f"{route.method.value}:{route.path}"
        self.routes[route_key] = route
        
        # Add circuit breaker if enabled
        if route.circuit_breaker and route.target_service:
            self.circuit_breakers[route.target_service] = CircuitBreaker()
        
        logger.info(f"Route added: {route_key}")
    
    def remove_route(self, path: str, method: HTTPMethod):
        """Remove a route"""
        route_key = f"{method.value}:{path}"
        if route_key in self.routes:
            del self.routes[route_key]
            logger.info(f"Route removed: {route_key}")
    
    def add_middleware(self, name: str, config: MiddlewareConfig):
        """Add middleware configuration"""
        self.middleware[name] = config
        logger.info(f"Middleware added: {name}")
    
    async def _handle_request(self, request: web.Request) -> web.Response:
        """Handle incoming request"""
        try:
            # Get route
            route_key = f"{request.method}:{request.path}"
            route = self.routes.get(route_key)
            
            if not route:
                return web.json_response(
                    {"error": "Route not found"},
                    status=404
                )
            
            # Apply middleware
            for middleware_name in route.middleware:
                if middleware_name in self.middleware:
                    middleware_config = self.middleware[middleware_name]
                    if middleware_config.enabled:
                        result = await self._apply_middleware(
                            middleware_name,
                            middleware_config,
                            request
                        )
                        if isinstance(result, web.Response):
                            return result
            
            # Rate limiting
            if route.rate_limit:
                client_ip = request.remote
                rate_key = f"{client_ip}:{route.path}"
                if not self.rate_limiter.is_allowed(rate_key, route.rate_limit):
                    return web.json_response(
                        {"error": "Rate limit exceeded"},
                        status=429
                    )
            
            # Authentication
            if route.auth_required:
                auth_result = await self._authenticate_request(request, route)
                if isinstance(auth_result, web.Response):
                    return auth_result
            
            # Check cache
            if route.cache_ttl > 0:
                cache_key = self._generate_cache_key(request)
                cached_response = self.cache.get(cache_key)
                if cached_response:
                    return web.json_response(cached_response)
            
            # Execute route
            response = await self._execute_route(route, request)
            
            # Cache response
            if route.cache_ttl > 0 and response.status == 200:
                cache_key = self._generate_cache_key(request)
                try:
                    response_data = await response.json()
                    self.cache.set(cache_key, response_data, route.cache_ttl)
                except:
                    pass  # Ignore JSON parsing errors
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return web.json_response(
                {"error": "Internal server error"},
                status=500
            )
    
    async def _apply_middleware(self, name: str, config: MiddlewareConfig, request: web.Request) -> Optional[web.Response]:
        """Apply middleware to request"""
        if name == "cors":
            return await self._cors_middleware(request, config.config)
        elif name == "logging":
            return await self._logging_middleware(request, config.config)
        elif name == "compression":
            return await self._compression_middleware(request, config.config)
        elif name == "security":
            return await self._security_middleware(request, config.config)
        
        return None
    
    async def _cors_middleware(self, request: web.Request, config: Dict[str, Any]) -> Optional[web.Response]:
        """CORS middleware"""
        if request.method == "OPTIONS":
            headers = {
                "Access-Control-Allow-Origin": config.get("allowed_origins", "*"),
                "Access-Control-Allow-Methods": config.get("allowed_methods", "GET, POST, PUT, DELETE"),
                "Access-Control-Allow-Headers": config.get("allowed_headers", "Content-Type, Authorization"),
                "Access-Control-Max-Age": "3600"
            }
            return web.Response(headers=headers)
        
        return None
    
    async def _logging_middleware(self, request: web.Request, config: Dict[str, Any]) -> Optional[web.Response]:
        """Logging middleware"""
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.path}")
        
        # Process request
        response = await self._handle_request(request)
        
        # Log response
        duration = time.time() - start_time
        logger.info(f"Response: {response.status} ({duration:.3f}s)")
        
        return response
    
    async def _compression_middleware(self, request: web.Request, config: Dict[str, Any]) -> Optional[web.Response]:
        """Compression middleware"""
        # Simple compression implementation
        return None
    
    async def _security_middleware(self, request: web.Request, config: Dict[str, Any]) -> Optional[web.Response]:
        """Security middleware"""
        # Add security headers
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block"
        }
        
        # Check for suspicious patterns
        user_agent = request.headers.get("User-Agent", "")
        if any(pattern in user_agent.lower() for pattern in ["bot", "crawler", "spider"]):
            if not config.get("allow_bots", False):
                return web.json_response(
                    {"error": "Bot access not allowed"},
                    status=403
                )
        
        return None
    
    async def _authenticate_request(self, request: web.Request, route: Route) -> Optional[web.Response]:
        """Authenticate request"""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return web.json_response(
                {"error": "Authorization header required"},
                status=401
            )
        
        try:
            # Extract token
            if auth_header.startswith("Bearer "):
                token = auth_header[7:]
            else:
                return web.json_response(
                    {"error": "Invalid authorization format"},
                    status=401
                )
            
            # Verify JWT token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            
            # Check roles if required
            if route.roles:
                user_roles = payload.get("roles", [])
                if not any(role in user_roles for role in route.roles):
                    return web.json_response(
                        {"error": "Insufficient permissions"},
                        status=403
                    )
            
            # Add user info to request
            request["user"] = payload
            
        except jwt.ExpiredSignatureError:
            return web.json_response(
                {"error": "Token expired"},
                status=401
            )
        except jwt.InvalidTokenError:
            return web.json_response(
                {"error": "Invalid token"},
                status=401
            )
        
        return None
    
    async def _execute_route(self, route: Route, request: web.Request) -> web.Response:
        """Execute route handler"""
        if route.route_type == RouteType.PROXY:
            return await self._proxy_request(route, request)
        elif route.route_type == RouteType.REDIRECT:
            return web.HTTPFound(route.target_url)
        elif route.route_type == RouteType.STATIC:
            return await self._serve_static(route, request)
        elif route.route_type == RouteType.FUNCTION:
            return await self._call_function(route, request)
        else:
            return web.json_response(
                {"error": "Unknown route type"},
                status=500
            )
    
    async def _proxy_request(self, route: Route, request: web.Request) -> web.Response:
        """Proxy request to target service"""
        if not route.target_url:
            return web.json_response(
                {"error": "No target URL configured"},
                status=500
            )
        
        # Check circuit breaker
        if route.circuit_breaker and route.target_service:
            circuit_breaker = self.circuit_breakers.get(route.target_service)
            if circuit_breaker and not circuit_breaker.can_execute():
                return web.json_response(
                    {"error": "Service temporarily unavailable"},
                    status=503
                )
        
        try:
            # Prepare request
            headers = dict(request.headers)
            headers.pop("Host", None)  # Remove host header
            
            # Make request
            async with self.session.request(
                method=request.method,
                url=route.target_url,
                headers=headers,
                data=await request.read(),
                params=request.query
            ) as response:
                response_data = await response.read()
                
                # Record success
                if route.circuit_breaker and route.target_service:
                    circuit_breaker = self.circuit_breakers.get(route.target_service)
                    if circuit_breaker:
                        circuit_breaker.record_success()
                
                return web.Response(
                    body=response_data,
                    status=response.status,
                    headers=response.headers
                )
        
        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            
            # Record failure
            if route.circuit_breaker and route.target_service:
                circuit_breaker = self.circuit_breakers.get(route.target_service)
                if circuit_breaker:
                    circuit_breaker.record_failure()
            
            return web.json_response(
                {"error": "Service unavailable"},
                status=503
            )
    
    async def _serve_static(self, route: Route, request: web.Request) -> web.Response:
        """Serve static content"""
        # Implementation for static file serving
        return web.json_response(
            {"error": "Static serving not implemented"},
            status=501
        )
    
    async def _call_function(self, route: Route, request: web.Request) -> web.Response:
        """Call function handler"""
        if not route.handler:
            return web.json_response(
                {"error": "No handler configured"},
                status=500
            )
        
        try:
            result = await route.handler(request)
            if isinstance(result, web.Response):
                return result
            else:
                return web.json_response(result)
        except Exception as e:
            logger.error(f"Function handler failed: {e}")
            return web.json_response(
                {"error": "Handler execution failed"},
                status=500
            )
    
    def _generate_cache_key(self, request: web.Request) -> str:
        """Generate cache key for request"""
        key_data = f"{request.method}:{request.path}:{request.query_string}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _setup_routes(self):
        """Setup default routes"""
        # Health check route
        health_route = Route(
            path="/health",
            method=HTTPMethod.GET,
            route_type=RouteType.FUNCTION,
            auth_required=False,
            handler=self._health_handler
        )
        self.add_route(health_route)
        
        # Metrics route
        metrics_route = Route(
            path="/metrics",
            method=HTTPMethod.GET,
            route_type=RouteType.FUNCTION,
            auth_required=False,
            handler=self._metrics_handler
        )
        self.add_route(metrics_route)
    
    def _setup_middleware(self):
        """Setup default middleware"""
        # CORS middleware
        cors_config = MiddlewareConfig(
            name="cors",
            enabled=True,
            config={
                "allowed_origins": "*",
                "allowed_methods": "GET, POST, PUT, DELETE, OPTIONS",
                "allowed_headers": "Content-Type, Authorization"
            }
        )
        self.add_middleware("cors", cors_config)
        
        # Logging middleware
        logging_config = MiddlewareConfig(
            name="logging",
            enabled=True,
            config={}
        )
        self.add_middleware("logging", logging_config)
        
        # Security middleware
        security_config = MiddlewareConfig(
            name="security",
            enabled=True,
            config={
                "allow_bots": False
            }
        )
        self.add_middleware("security", security_config)
    
    async def _health_handler(self, request: web.Request) -> web.Response:
        """Health check handler"""
        return web.json_response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "routes": len(self.routes),
            "middleware": len(self.middleware)
        })
    
    async def _metrics_handler(self, request: web.Request) -> web.Response:
        """Metrics handler"""
        return web.json_response({
            "routes": len(self.routes),
            "middleware": len(self.middleware),
            "circuit_breakers": len(self.circuit_breakers),
            "cache_size": len(self.cache.cache),
            "rate_limits": len(self.rate_limiter.rate_limits)
        })

# Global API Gateway instance
api_gateway = APIGateway()

# Helper functions
def add_route(
    path: str,
    method: HTTPMethod,
    target_url: str = None,
    target_service: str = None,
    auth_required: bool = True,
    rate_limit: int = None,
    cache_ttl: int = 0
):
    """Helper function to add a route"""
    route = Route(
        path=path,
        method=method,
        route_type=RouteType.PROXY,
        target_url=target_url,
        target_service=target_service,
        auth_required=auth_required,
        rate_limit=rate_limit,
        cache_ttl=cache_ttl
    )
    api_gateway.add_route(route)

def add_function_route(
    path: str,
    method: HTTPMethod,
    handler: Callable,
    auth_required: bool = True
):
    """Helper function to add a function route"""
    route = Route(
        path=path,
        method=method,
        route_type=RouteType.FUNCTION,
        handler=handler,
        auth_required=auth_required
    )
    api_gateway.add_route(route)

if __name__ == "__main__":
    # Example usage
    async def main():
        # Start API Gateway
        await api_gateway.start()
        
        # Add some routes
        add_route(
            path="/api/v1/users",
            method=HTTPMethod.GET,
            target_url="http://localhost:8002/users",
            target_service="user-service",
            rate_limit=100
        )
        
        add_route(
            path="/api/v1/auth/login",
            method=HTTPMethod.POST,
            target_url="http://localhost:8001/login",
            target_service="auth-service",
            auth_required=False,
            rate_limit=10
        )
        
        # Keep running
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            await api_gateway.stop()
    
    asyncio.run(main())
