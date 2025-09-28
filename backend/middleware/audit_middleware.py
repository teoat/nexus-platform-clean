#!/usr/bin/env python3
"""
NEXUS Platform - Audit Logging Middleware
Automatic audit logging for all API requests and responses
"""

import json
import logging
import time
from typing import Callable, Dict, Any, Optional
from datetime import datetime, timezone

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from services.audit_logging import AuditLogQueryEngine, AuditLogLevel, OperationType

# Configure logging
logger = logging.getLogger(__name__)

# Initialize audit engine
audit_engine = AuditLogQueryEngine()


class AuditMiddleware:
    """
    Middleware for automatic audit logging of API requests and responses
    """

    def __init__(self, app: Callable):
        self.app = app
        # Routes to exclude from audit logging
        self.exclude_paths = {
            "/health",
            "/api/health",
            "/metrics",
            "/api/metrics",
            "/favicon.ico",
            "/docs",
            "/redoc",
            "/openapi.json"
        }

        # Sensitive headers to mask in logs
        self.sensitive_headers = {
            "authorization",
            "x-api-key",
            "x-auth-token",
            "cookie",
            "set-cookie"
        }

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create request object
        request = Request(scope, receive)

        # Skip audit logging for excluded paths
        if request.url.path in self.exclude_paths:
            await self.app(scope, receive, send)
            return

        # Extract request information
        start_time = time.time()
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")
        content_type = request.headers.get("content-type", "")

        # Extract user information (if available)
        user_id = self._extract_user_id(request)

        # Log request start
        request_id = f"{int(start_time * 1000000)}"

        # Prepare response capture
        response_body = None
        response_status = None
        response_headers = {}

        async def capture_response(message):
            nonlocal response_body, response_status, response_headers

            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = dict(message.get("headers", []))

            elif message["type"] == "http.response.body":
                if message.get("body"):
                    try:
                        # Try to parse JSON response for logging
                        response_body = json.loads(message["body"].decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # If not JSON, log as text or truncate if too large
                        body_text = message["body"].decode(errors='ignore')
                        if len(body_text) > 1000:
                            response_body = body_text[:1000] + "..."
                        else:
                            response_body = body_text

            await send(message)

        # Process the request
        try:
            await self.app(scope, receive, capture_response)

            # Calculate response time
            response_time = time.time() - start_time

            # Determine operation type based on HTTP method
            operation_type = self._map_http_method_to_operation(method)

            # Prepare audit details
            audit_details = {
                "request": {
                    "method": method,
                    "path": path,
                    "query_params": self._sanitize_query_params(query_params),
                    "content_type": content_type,
                    "user_agent": user_agent[:200] if user_agent else None,  # Truncate if too long
                },
                "response": {
                    "status_code": response_status,
                    "response_time_ms": round(response_time * 1000, 2),
                    "content_type": response_headers.get(b"content-type", b"").decode() if response_headers.get(b"content-type") else None,
                },
                "performance": {
                    "response_time_seconds": response_time,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            }

            # Add response body for error responses or specific endpoints
            if response_status and (response_status >= 400 or self._should_log_response_body(path)):
                if response_body:
                    audit_details["response"]["body"] = self._sanitize_response_body(response_body)

            # Determine log level based on response status
            log_level = AuditLogLevel.INFO
            if response_status and response_status >= 500:
                log_level = AuditLogLevel.ERROR
            elif response_status and response_status >= 400:
                log_level = AuditLogLevel.WARNING

            # Log the API operation
            await audit_engine.log_operation(
                operation=operation_type.value,
                entity_type="APIEndpoint",
                entity_id=f"{method} {path}",
                details=audit_details,
                performed_by=user_id or "anonymous",
                context="api_request",
                log_level=log_level,
                ip_address=client_ip,
                user_agent=user_agent,
                session_id=request_id,
            )

        except Exception as e:
            # Log failed requests
            response_time = time.time() - start_time

            audit_details = {
                "request": {
                    "method": method,
                    "path": path,
                    "query_params": self._sanitize_query_params(query_params),
                    "content_type": content_type,
                    "user_agent": user_agent[:200] if user_agent else None,
                },
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "response_time_ms": round(response_time * 1000, 2),
                },
                "performance": {
                    "response_time_seconds": response_time,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            }

            await audit_engine.log_operation(
                operation=OperationType.SYSTEM.value,
                entity_type="APIEndpoint",
                entity_id=f"{method} {path}",
                details=audit_details,
                performed_by=user_id or "anonymous",
                context="api_error",
                log_level=AuditLogLevel.ERROR,
                ip_address=client_ip,
                user_agent=user_agent,
                session_id=request_id,
            )

            # Re-raise the exception
            raise

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in case of multiple
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fall back to direct client
        if request.client:
            return request.client.host

        return "unknown"

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request (JWT token, etc.)"""
        try:
            # Check for Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, you'd decode the JWT to get user info
                # For now, we'll just indicate it's authenticated
                return "authenticated_user"

            # Check for user ID in headers (set by auth middleware)
            user_id = request.headers.get("x-user-id")
            if user_id:
                return user_id

        except Exception as e:
            logger.debug(f"Error extracting user ID: {e}")

        return None

    def _map_http_method_to_operation(self, method: str) -> OperationType:
        """Map HTTP method to audit operation type"""
        method_mapping = {
            "GET": OperationType.READ,
            "POST": OperationType.CREATE,
            "PUT": OperationType.UPDATE,
            "PATCH": OperationType.UPDATE,
            "DELETE": OperationType.DELETE,
        }
        return method_mapping.get(method.upper(), OperationType.SYSTEM)

    def _sanitize_query_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize query parameters for logging"""
        sanitized = {}
        sensitive_keys = {"password", "token", "key", "secret", "api_key", "apikey"}

        for key, value in params.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "***MASKED***"
            else:
                # Truncate long values
                if isinstance(value, str) and len(value) > 100:
                    sanitized[key] = value[:100] + "..."
                else:
                    sanitized[key] = value

        return sanitized

    def _sanitize_response_body(self, body: Any) -> Any:
        """Sanitize response body for logging"""
        if isinstance(body, dict):
            sanitized = {}
            sensitive_keys = {"password", "token", "key", "secret", "api_key", "apikey", "credit_card"}

            for key, value in body.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = "***MASKED***"
                elif isinstance(value, (dict, list)):
                    sanitized[key] = self._sanitize_response_body(value)
                elif isinstance(value, str) and len(value) > 500:
                    sanitized[key] = value[:500] + "..."
                else:
                    sanitized[key] = value

            return sanitized
        elif isinstance(body, list):
            return [self._sanitize_response_body(item) for item in body[:10]]  # Limit array items
        else:
            return body

    def _should_log_response_body(self, path: str) -> bool:
        """Determine if response body should be logged for this endpoint"""
        # Log response bodies for important endpoints
        important_endpoints = {
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/admin",
            "/api/v1/audit",
        }

        return any(path.startswith(endpoint) for endpoint in important_endpoints)


def create_audit_middleware(app):
    """
    Factory function to create audit middleware
    """
    return AuditMiddleware(app)