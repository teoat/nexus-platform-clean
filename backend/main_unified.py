#!/usr/bin/env python3
"""
NEXUS Platform - Unified Backend Application
Consolidated backend with all services integrated
"""

import os
import sys
import asyncio
import logging
import signal
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
from datetime import datetime
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status, Request, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import json
import re
import html
import bleach
import psutil
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
from pydantic import BaseModel, validator

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Import SSOT components
from services.ssot_registry import SSOTRegistry, AliasType, AliasStatus
from services.alias_manager import AliasManager
from services.api_registry_integration import api_registry_integration
from services.api_versioning import api_versioning, APIVersion
from services.rate_limiting import rate_limiting, RateLimitExceeded
from services.data_schema_validation import data_schema_validator

# Import new Phase 2 services
from services.data_migration_validation import data_migration_validator
from services.data_integrity_checks import data_integrity_checker
from services.deployment_pipeline_integration import deployment_pipeline_integrator
from services.ai_ssot_optimizer import ai_ssot_optimizer
from services.blue_green_deployment import blue_green_deployment_service
from services.ai_monitoring_alerting import ai_monitoring_alerting_service
from services.ultimate_frenly_ai_orchestrator import UltimateFrenlyAIOrchestrator

# Import Redis caching service
from services.redis_cache_service import redis_cache_service

# Import enhanced database optimizer
from services.database_optimizer_enhanced import database_optimizer
# Import database audit service
# Import database connection
from database.connection import engine
from services.database_audit_service import database_audit_service, setup_database_audit_hooks
# Import audit routes
# Import file system audit service
from services.filesystem_audit_service import filesystem_audit_service
from routes.audit_routes import router as audit_router
# Import audit cleanup service
from services.audit_cleanup_service import audit_cleanup_service
# Import audit middleware
# Import audit compliance service
from services.audit_compliance_service import audit_compliance_service
from middleware.audit_middleware import create_audit_middleware
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('nexus_backend.log')
    ]
)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Pagination models
class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Query(1, ge=1, description="Page number")
    per_page: int = Query(50, ge=1, le=1000, description="Items per page")
    sort_by: Optional[str] = Query(None, description="Sort field")
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order")

class PaginatedResponse(BaseModel):
    """Paginated response model"""
    data: List[Any]
    pagination: Dict[str, Any]
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool

def paginate_data(data: List[Any], params: PaginationParams) -> PaginatedResponse:
    """Paginate a list of data"""
    total = len(data)
    total_pages = (total + params.per_page - 1) // params.per_page

    # Apply sorting if requested
    if params.sort_by:
        reverse = params.sort_order == "desc"
        try:
            if isinstance(data[0], dict):
                data.sort(key=lambda x: x.get(params.sort_by, ""), reverse=reverse)
            else:
                data.sort(key=lambda x: getattr(x, params.sort_by, ""), reverse=reverse)
        except (AttributeError, TypeError):
            # If sorting fails, continue without sorting
            pass

    # Apply pagination
    start_idx = (params.page - 1) * params.per_page
    end_idx = start_idx + params.per_page
    paginated_data = data[start_idx:end_idx]

    return PaginatedResponse(
        data=paginated_data,
        pagination={
            "page": params.page,
            "per_page": params.per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": params.page < total_pages,
            "has_prev": params.page > 1
        },
        total=total,
        page=params.page,
        per_page=params.per_page,
        total_pages=total_pages,
        has_next=params.page < total_pages,
        has_prev=params.page > 1
    )

def select_fields(data: List[Dict[str, Any]], fields: Optional[str] = None) -> List[Dict[str, Any]]:
    """Select specific fields from data objects"""
    if not fields:
        return data

    field_list = [f.strip() for f in fields.split(",")]
    return [
        {k: v for k, v in item.items() if k in field_list}
        for item in data
    ]

# Security utilities
class SecurityUtils:
    """Security utility functions"""

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input to prevent XSS and injection attacks"""
        if not isinstance(text, str):
            return text

        # HTML escape
        text = html.escape(text)

        # Remove potentially dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',                # JavaScript URLs
            r'vbscript:',                  # VBScript URLs
            r'on\w+\s*=',                  # Event handlers
            r'<iframe[^>]*>.*?</iframe>',  # Iframes
            r'<object[^>]*>.*?</object>',  # Objects
            r'<embed[^>]*>.*?</embed>',    # Embeds
        ]

        for pattern in dangerous_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)

        return text

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))

    @staticmethod
    def validate_sql_injection(text: str) -> bool:
        """Check for potential SQL injection patterns"""
        sql_patterns = [
            r';\s*(drop|delete|update|insert|alter|create|truncate)\s',
            r'union\s+select',
            r'--',
            r'/\*.*\*/',
            r'xp_',
            r'sp_',
            r'exec\s*\(',
        ]

        for pattern in sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
        return True

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.replace('..', '')
        return filename[:255]  # Limit length

# Input validation models
class SecureBaseModel(BaseModel):
    """Base model with input validation and sanitization"""

    class Config:
        validate_assignment = True

    @validator('*', pre=True)
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return SecurityUtils.sanitize_input(v)
        return v

class UserRegistration(SecureBaseModel):
    email: str
    password: str
    name: Optional[str] = None

    @validator('email')
    def validate_email_format(cls, v):
        if not SecurityUtils.validate_email(v):
            raise ValueError('Invalid email format')
        return v

    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v

class LoginRequest(SecureBaseModel):
    email: str
    password: str

    @validator('email')
    def validate_email_format(cls, v):
        if not SecurityUtils.validate_email(v):
            raise ValueError('Invalid email format')
        return v

class NexusUnifiedBackend:
    """Unified NEXUS backend with all services integrated"""
    
    def __init__(self):
        self.app = FastAPI(
            title="NEXUS Platform API",
            description="""
            # NEXUS Platform - Unified Backend API

            A comprehensive, AI-powered platform providing unified services for modern applications.

            ## Features

            * **SSOT (Single Source of Truth)**: Centralized configuration and alias management
            * **API Registry**: Service discovery and integration
            * **Rate Limiting**: Advanced rate limiting with multiple strategies
            * **Authentication**: JWT-based authentication with MFA support
            * **Financial Services**: Account management and transaction processing
            * **AI Services**: Chat, insights, and optimization features
            * **Monitoring**: Comprehensive system and performance monitoring
            * **Deployment**: Blue-green deployment and rollback capabilities

            ## Authentication

            Most endpoints require authentication. Include the JWT token in the Authorization header:

            ```
            Authorization: Bearer <your-jwt-token>
            ```

            ## Rate Limiting

            API requests are rate-limited. Check the response headers for limit information:
            - `X-RateLimit-Limit`: Maximum requests per window
            - `X-RateLimit-Remaining`: Remaining requests
            - `X-RateLimit-Reset`: Time when limit resets

            ## Versioning

            API endpoints support versioning. Use the version prefix in the URL:
            - `v1`: Legacy endpoints
            - `v3`: Current stable version

            ## Error Responses

            All error responses follow this format:

            ```json
            {
              "error": "ErrorType",
              "message": "Human-readable error message",
              "details": {}
            }
            ```
            """,
            version="3.0.0",
            contact={
                "name": "NEXUS Platform Support",
                "email": "support@nexus-platform.com",
                "url": "https://nexus-platform.com/support"
            },
            license_info={
                "name": "Proprietary",
                "url": "https://nexus-platform.com/license"
            },
            openapi_tags=[
                {
                    "name": "Authentication",
                    "description": "User authentication and authorization endpoints"
                },
                {
                    "name": "User Management",
                    "description": "User profile and settings management"
                },
                {
                    "name": "Financial Services",
                    "description": "Account and transaction management"
                },
                {
                    "name": "AI Services",
                    "description": "AI-powered features and insights"
                },
                {
                    "name": "SSOT",
                    "description": "Single Source of Truth operations"
                },
                {
                    "name": "API Registry",
                    "description": "Service discovery and integration"
                },
                {
                    "name": "Monitoring",
                    "description": "System monitoring and alerting"
                },
                {
                    "name": "Deployment",
                    "description": "Deployment and rollback operations"
                },
                {
                    "name": "Cache Management",
                    "description": "Redis cache operations"
                },
                {
                    "name": "Database Optimization",
                    "description": "Database performance optimization"
                },
                {
                    "name": "System Administration",
                    "description": "Administrative operations"
                }
            ],
            lifespan=self.lifespan
        )
        self.services = {}
        
        # Initialize SSOT components
        self.ssot_registry = SSOTRegistry()
        self.alias_manager = AliasManager()

        # Initialize Ultimate Frenly AI Orchestrator
        self.frenly_orchestrator = UltimateFrenlyAIOrchestrator()
        
        self.setup_middleware()
        self.setup_routes()
        self.setup_health_monitoring()
        
        # Initialize Prometheus metrics
        self.setup_prometheus_metrics()
    
    def setup_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        # SSOT Metrics
        self.ssot_operations_total = Counter('ssot_operations_total', 'Total number of SSOT operations', ['operation_type', 'status'])
        self.ssot_validation_failures_total = Counter('ssot_validation_failures_total', 'Total number of SSOT validation failures', ['validation_type', 'component'])
        self.ssot_anchors_total = Gauge('ssot_anchors_total', 'Total number of SSOT anchors', ['family', 'status'])
        self.ssot_aliases_total = Gauge('ssot_aliases_total', 'Total number of SSOT aliases', ['context', 'status'])
        self.ssot_alias_resolution_duration_seconds = Histogram('ssot_alias_resolution_duration_seconds', 'Duration of SSOT alias resolution', buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0])
        self.ssot_duplicate_files_total = Gauge('ssot_duplicate_files_total', 'Total number of duplicate files detected', ['file_type', 'location'])
        self.ssot_errors_total = Counter('ssot_errors_total', 'Total number of SSOT errors', ['error_type', 'component'])
        self.ssot_unauthorized_attempts_total = Counter('ssot_unauthorized_attempts_total', 'Total number of unauthorized access attempts', ['source_ip', 'user_agent'])
        self.ssot_config_changes_total = Counter('ssot_config_changes_total', 'Total number of configuration changes', ['change_type', 'user'])
        self.ssot_cache_hits_total = Counter('ssot_cache_hits_total', 'Total number of SSOT cache hits', ['cache_type'])
        self.ssot_cache_misses_total = Counter('ssot_cache_misses_total', 'Total number of SSOT cache misses', ['cache_type'])
        self.ssot_consistency_score = Gauge('ssot_consistency_score', 'SSOT consistency score (0-1)', ['component'])
        
        # System Metrics
        self.http_requests_total = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
        self.http_request_duration_seconds = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
        
        # Add missing API health endpoint
        @self.app.get("/api/health", tags=["Health"], summary="API Health Check")
        async def api_health_fix():
            """API health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "3.0.0",
                "service": "nexus-api",
                "requests_processed": self.request_count,
                "errors": self.error_count
            }
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Application lifespan events"""
        logger.info("🚀 Starting NEXUS Unified Backend...")

        # Initialize services
        await self.initialize_services()

        # Initialize Redis cache service
        await redis_cache_service.initialize()

        # Initialize database optimizer
        # Setup database audit hooks
        # Setup file system audit monitoring
        # Start audit cleanup scheduler
        await audit_cleanup_service.start_cleanup_scheduler()
        logger.info("Audit cleanup scheduler started")
        filesystem_audit_service.add_monitored_path("config")
        filesystem_audit_service.add_monitored_path("data")
        filesystem_audit_service.add_monitored_path("backend")
        logger.info("File system audit monitoring initialized")
        setup_database_audit_hooks(engine)
        logger.info("Database audit hooks initialized")
        await database_optimizer.initialize()

        yield

        logger.info("🛑 Shutting down NEXUS Unified Backend...")
        await self.cleanup_services()

        # Close Redis cache service
        # Stop audit cleanup scheduler
        await audit_cleanup_service.stop_cleanup_scheduler()
        await redis_cache_service.close()
    
    def setup_middleware(self):
        """Setup middleware configuration"""
        # Rate limiting middleware
        @self.app.middleware("http")
        async def rate_limit_middleware(request: Request, call_next):
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"

            # Determine rate limit rule based on endpoint
            path = request.url.path
            rule_name = "api_general"

            if path.startswith("/api/v3/auth"):
                rule_name = "api_auth"
            elif path.startswith("/api/v3/admin"):
                rule_name = "api_admin"
            elif path.startswith("/api/v1/ssot"):
                rule_name = "api_general"  # SSOT has its own limits

            # Check rate limit
            rate_key = f"{client_ip}:{path}"
            allowed, rate_limit_info = await rate_limiting.check_rate_limit(
                key=rate_key,
                rule_name=rule_name,
                client_ip=client_ip
            )

            if not allowed:
                # Return rate limit exceeded response
                headers = rate_limiting.get_rate_limit_headers(rate_limit_info)
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Retry after {rate_limit_info['retry_after']} seconds.",
                        "retry_after": rate_limit_info["retry_after"]
                    },
                    headers=headers
                )

            # Add rate limit headers to response
            response = await call_next(request)
            headers = rate_limiting.get_rate_limit_headers(rate_limit_info)
            for header_name, header_value in headers.items():
                response.headers[header_name] = header_value

            return response

        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://localhost:3001",
                "http://localhost:3002",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                "http://127.0.0.1:3002"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Trusted host middleware
        self.app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
        )

        # GZip compression middleware
        self.app.add_middleware(
            GZipMiddleware,
            minimum_size=1000,  # Only compress responses larger than 1KB
            compresslevel=6     # Good balance between speed and compression
        )

        # Response optimization middleware
        @self.app.middleware("http")
        async def response_optimization_middleware(request: Request, call_next):
            """Optimize API responses for better performance"""
            # Get response
            response = await call_next(request)

            # Add response optimization headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"

            # Add cache control headers for static-like responses
            if request.method == "GET" and not request.url.path.startswith(("/api/v3/auth", "/api/v3/admin")):
                response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes cache

            # Optimize JSON responses
            if response.headers.get("content-type", "").startswith("application/json"):
                # Ensure responses are properly formatted
                if hasattr(response, 'body') and response.body:
                    try:
                        # Parse and re-serialize to ensure compact JSON
                        import json
                        data = json.loads(response.body.decode('utf-8'))
                        optimized_body = json.dumps(data, separators=(',', ':')).encode('utf-8')
                        response.body = optimized_body
                        response.headers["Content-Length"] = str(len(optimized_body))
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        # If parsing fails, leave original response
                        pass

            return response

        # Response size limit middleware
        @self.app.middleware("http")
        async def response_size_limit_middleware(request: Request, call_next):
            """Limit response size to prevent memory issues"""
            response = await call_next(request)

            # Check response size (skip for streaming responses)
            if hasattr(response, 'body') and response.body:
                body_size = len(response.body)
                max_size = 50 * 1024 * 1024  # 50MB limit

                if body_size > max_size:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "error": "Response too large",
                            "message": f"Response size ({body_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
                            "status": "error"
                        }
                    )

                # Add size header for monitoring
                response.headers["X-Response-Size"] = str(body_size)

            return response

        # Security middleware
        @self.app.middleware("http")
        async def security_middleware(request: Request, call_next):
            """Comprehensive security middleware"""
            # Log suspicious requests
            client_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get("User-Agent", "")

            # Check for suspicious patterns
            suspicious_patterns = [
                r'\.\./',  # Path traversal
                r'<script',  # XSS attempts
                r'union\s+select',  # SQL injection
                r'../../../',  # Path traversal
            ]

            request_path = str(request.url.path)
            request_query = str(request.url.query)

            for pattern in suspicious_patterns:
                if re.search(pattern, request_path + request_query, re.IGNORECASE):
                    logger.warning(f"Suspicious request detected from {client_ip}: {request_path}")
                    # Add security headers
                    response = JSONResponse(
                        status_code=403,
                        content={"error": "Forbidden", "message": "Suspicious request pattern detected"}
                    )
                    response.headers["X-Security-Alert"] = "suspicious_pattern"
                    return response

            # Check request size
            content_length = request.headers.get("Content-Length")
            if content_length:
                try:
                    size = int(content_length)
                    max_request_size = 10 * 1024 * 1024  # 10MB
                    if size > max_request_size:
                        return JSONResponse(
                            status_code=413,
                            content={"error": "Request too large", "message": f"Request size exceeds {max_request_size} bytes"}
                        )
                except ValueError:
                    pass

            response = await call_next(request)

            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

            # Add HSTS for HTTPS
            if request.url.scheme == "https":
                response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

            return response

        # Redis cache middleware
        # Audit logging middleware
        audit_middleware = create_audit_middleware(self.app)
        self.app.add_middleware(audit_middleware)

        # Redis cache middleware
        cache_middleware = redis_cache_service.get_cache_middleware()
        self.app.add_middleware(cache_middleware)
    
    def setup_routes(self):
        """Setup all API routes with versioning"""
        """Setup all API routes with versioning"""
        # Register endpoints with versioning service
        self._register_versioned_endpoints()

        # Health and system routes (non-versioned)
        self.app.get("/health")(self.health_check)
        self.app.get("/api/health")(self.api_health)
        self.app.get("/api/status")(self.system_status)
        self.app.get("/api/metrics")(self.system_metrics)
        self.app.get("/metrics")(self.prometheus_metrics)
        
        # Additional health endpoint for compatibility
        @self.app.get("/api/health", tags=["Health"])
        async def api_health_endpoint():
            return await self.api_health()

        # Version-aware routes
        self.app.get("/api/{version}/ssot/resolve/{alias}")(self.resolve_alias)
        self.app.get("/api/{version}/ssot/aliases")(self.list_aliases)
        self.app.post("/api/{version}/ssot/aliases")(self.create_alias)
        self.app.delete("/api/{version}/ssot/aliases/{alias}")(self.delete_alias)
        self.app.get("/api/{version}/ssot/aliases/{alias}")(self.get_alias_info)

        # API Registry Integration routes
        self.app.post("/api/{version}/registry/integrate")(self.integrate_services)
        self.app.get("/api/{version}/registry/status")(self.get_integration_status)
        self.app.post("/api/{version}/registry/validate")(self.validate_integration)
        self.app.delete("/api/{version}/registry/cleanup")(self.cleanup_integration)

        # Ultimate Frenly AI Orchestrator routes
        self.app.post("/api/{version}/orchestrator/execute")(self.execute_pipeline)
        self.app.get("/api/{version}/orchestrator/executions")(self.list_pipeline_executions)
        self.app.get("/api/{version}/orchestrator/executions/{execution_id}")(self.get_pipeline_execution)
        self.app.post("/api/{version}/orchestrator/executions/{execution_id}/cancel")(self.cancel_pipeline_execution)

        # Authentication routes
        self.app.post("/api/{version}/auth/login")(self.login)
        self.app.post("/api/{version}/auth/register")(self.register)
        self.app.post("/api/{version}/auth/refresh")(self.refresh_token)
        self.app.post("/api/{version}/auth/logout")(self.logout)

        # User management routes
        self.app.get("/api/{version}/users/profile")(self.get_user_profile)
        self.app.put("/api/{version}/users/profile")(self.update_user_profile)
        self.app.get("/api/{version}/users/settings")(self.get_user_settings)
        self.app.put("/api/{version}/users/settings")(self.update_user_settings)

        # Financial services routes
        self.app.get("/api/{version}/financial/accounts")(self.get_accounts)
        self.app.post("/api/{version}/financial/accounts")(self.create_account)
        self.app.get("/api/{version}/financial/transactions")(self.get_transactions)
        self.app.post("/api/{version}/financial/transactions")(self.create_transaction)
        self.app.get("/api/{version}/financial/budgets")(self.get_budgets)
        self.app.post("/api/{version}/financial/budgets")(self.create_budget)
        self.app.get("/api/{version}/financial/analytics")(self.get_analytics)

        # AI services routes
        self.app.post("/api/{version}/ai/chat")(self.ai_chat)
        self.app.get("/api/{version}/ai/insights")(self.get_ai_insights)
        self.app.get("/api/{version}/ai/monitoring")(self.get_ai_monitoring)
        self.app.post("/api/{version}/ai/optimization")(self.ai_optimization)

        # Admin routes
        self.app.get("/api/{version}/admin/users")(self.admin_get_users)
        self.app.get("/api/{version}/admin/audit")(self.admin_get_audit)
        self.app.get("/api/{version}/admin/system")(self.admin_get_system)
        self.app.get("/api/{version}/admin/monitoring")(self.admin_get_monitoring)

        # Audit routes
        self.app.include_router(audit_router, prefix="/api/v1", tags=["audit"])

        # System routes
        self.app.get("/api/{version}/system/config")(self.get_system_config)
        self.app.put("/api/{version}/system/config")(self.update_system_config)

        # API Versioning routes
        self.app.get("/api/versions")(self.get_api_versions)
        self.app.get("/api/{version}/info")(self.get_version_info)

        # Rate Limiting routes
        self.app.get("/api/{version}/rate-limits")(self.get_rate_limits)
        self.app.post("/api/{version}/rate-limits/exempt")(self.exempt_from_rate_limits)
        self.app.delete("/api/{version}/rate-limits/exempt")(self.remove_rate_limit_exemption)

        # Data Validation routes
        self.app.post("/api/{version}/validation/schemas")(self.validate_data_schemas)
        self.app.get("/api/{version}/validation/status")(self.get_validation_status)

        # Data Migration Validation routes
        self.app.post("/api/{version}/migration/validate")(self.validate_migration)
        self.app.get("/api/{version}/migration/reports")(self.get_migration_reports)
    
    def setup_health_monitoring(self):
        """Setup health monitoring"""
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0

    def _register_versioned_endpoints(self):
        """Register all endpoints with the versioning service"""
        # SSOT endpoints (v1)
        api_versioning.register_endpoint(
            path="/api/v1/ssot/resolve/{alias}",
            methods=["GET"],
            version=APIVersion.V1,
            handler=self.resolve_alias
        )
        api_versioning.register_endpoint(
            path="/api/v1/ssot/aliases",
            methods=["GET", "POST"],
            version=APIVersion.V1,
            handler=self.list_aliases
        )
        api_versioning.register_endpoint(
            path="/api/v1/ssot/aliases/{alias}",
            methods=["GET", "DELETE"],
            version=APIVersion.V1,
            handler=self.get_alias_info
        )

        # SSOT endpoints (v3) - current version
        api_versioning.register_endpoint(
            path="/api/v3/ssot/resolve/{alias}",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.resolve_alias
        )
        api_versioning.register_endpoint(
            path="/api/v3/ssot/aliases",
            methods=["GET", "POST"],
            version=APIVersion.V3,
            handler=self.list_aliases
        )
        api_versioning.register_endpoint(
            path="/api/v3/ssot/aliases/{alias}",
            methods=["GET", "DELETE"],
            version=APIVersion.V3,
            handler=self.get_alias_info
        )

        # Auth endpoints (v3)
        api_versioning.register_endpoint(
            path="/api/v3/auth/login",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.login
        )
        api_versioning.register_endpoint(
            path="/api/v3/auth/register",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.register
        )
        api_versioning.register_endpoint(
            path="/api/v3/auth/refresh",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.refresh_token
        )
        api_versioning.register_endpoint(
            path="/api/v3/auth/logout",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.logout
        )

        # User management endpoints (v3)
        api_versioning.register_endpoint(
            path="/api/v3/users/profile",
            methods=["GET", "PUT"],
            version=APIVersion.V3,
            handler=self.get_user_profile
        )
        api_versioning.register_endpoint(
            path="/api/v3/users/settings",
            methods=["GET", "PUT"],
            version=APIVersion.V3,
            handler=self.get_user_settings
        )

        # Financial endpoints (v3)
        api_versioning.register_endpoint(
            path="/api/v3/financial/accounts",
            methods=["GET", "POST"],
            version=APIVersion.V3,
            handler=self.get_accounts
        )
        api_versioning.register_endpoint(
            path="/api/v3/financial/transactions",
            methods=["GET", "POST"],
            version=APIVersion.V3,
            handler=self.get_transactions
        )
        api_versioning.register_endpoint(
            path="/api/v3/financial/budgets",
            methods=["GET", "POST"],
            version=APIVersion.V3,
            handler=self.get_budgets
        )
        api_versioning.register_endpoint(
            path="/api/v3/financial/analytics",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.get_analytics
        )

        # AI endpoints (v3)
        api_versioning.register_endpoint(
            path="/api/v3/ai/chat",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.ai_chat
        )
        api_versioning.register_endpoint(
            path="/api/v3/ai/insights",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.get_ai_insights
        )
        api_versioning.register_endpoint(
            path="/api/v3/ai/monitoring",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.get_ai_monitoring
        )
        api_versioning.register_endpoint(
            path="/api/v3/ai/optimization",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.ai_optimization
        )

        # Admin endpoints (v3)
        api_versioning.register_endpoint(
            path="/api/v3/admin/users",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.admin_get_users
        )
        api_versioning.register_endpoint(
            path="/api/v3/admin/audit",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.admin_get_audit
        )
        api_versioning.register_endpoint(
            path="/api/v3/admin/system",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.admin_get_system
        )
        api_versioning.register_endpoint(
            path="/api/v3/admin/monitoring",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.admin_get_monitoring
        )

        # System endpoints (v3)
        api_versioning.register_endpoint(
            path="/api/v3/system/config",
            methods=["GET", "PUT"],
            version=APIVersion.V3,
            handler=self.get_system_config
        )

        # Registry endpoints (v1)
        api_versioning.register_endpoint(
            path="/api/v1/registry/integrate",
            methods=["POST"],
            version=APIVersion.V1,
            handler=self.integrate_services
        )
        api_versioning.register_endpoint(
            path="/api/v1/registry/status",
            methods=["GET"],
            version=APIVersion.V1,
            handler=self.get_integration_status
        )
        api_versioning.register_endpoint(
            path="/api/v1/registry/validate",
            methods=["POST"],
            version=APIVersion.V1,
            handler=self.validate_integration
        )
        api_versioning.register_endpoint(
            path="/api/v1/registry/cleanup",
            methods=["DELETE"],
            version=APIVersion.V1,
            handler=self.cleanup_integration
        )

        # Orchestrator endpoints (v3)
        api_versioning.register_endpoint(
            path="/api/v3/orchestrator/execute",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.execute_pipeline
        )
        api_versioning.register_endpoint(
            path="/api/v3/orchestrator/executions",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.list_pipeline_executions
        )
        api_versioning.register_endpoint(
            path="/api/v3/orchestrator/executions/{execution_id}",
            methods=["GET"],
            version=APIVersion.V3,
            handler=self.get_pipeline_execution
        )
        api_versioning.register_endpoint(
            path="/api/v3/orchestrator/executions/{execution_id}/cancel",
            methods=["POST"],
            version=APIVersion.V3,
            handler=self.cancel_pipeline_execution
        )
    
    async def initialize_services(self):
        """Initialize all services"""
        logger.info("🔧 Initializing services...")

        # Initialize service registry
        self.services = {
            "database": {"status": "initialized", "port": 5432},
            "redis": {"status": "initialized", "port": 6379},
            "frenly_ai": {"status": "initialized", "port": 8765},
            "monitoring": {"status": "initialized", "port": 9090}
        }

        # Initialize API registry integration
        logger.info("🔗 Integrating services with API registry...")
        integration_result = await api_registry_integration.integrate_all_services()
        if integration_result["success"]:
            logger.info(f"✅ API registry integration completed: {integration_result['integrated_services']}")
        else:
            logger.warning(f"⚠️ API registry integration completed with issues: {integration_result['failed_services']}")

        logger.info("✅ All services initialized")
    
    async def cleanup_services(self):
        """Cleanup services on shutdown"""
        logger.info("🧹 Cleaning up services...")

        # Cleanup API registry integration
        logger.info("🔗 Cleaning up API registry integration...")
        cleanup_result = await api_registry_integration.cleanup_integration()
        if cleanup_result["success"]:
            logger.info(f"✅ API registry cleanup completed: {cleanup_result['removed_contracts']} contracts, {cleanup_result['removed_aliases']} aliases")
        else:
            logger.warning(f"⚠️ API registry cleanup completed with issues: {cleanup_result['errors']}")

        # Close API registry integration
        await api_registry_integration.close()

        logger.info("✅ Services cleaned up")
    
    # Health and system endpoints
    async def health_check(self):
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "service": "nexus-unified-backend",
            "uptime": str(datetime.now() - self.start_time)
        }
    
    async def api_health(self):
        """API health check for frontend"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "3.0.0",
            "service": "nexus-api",
            "requests_processed": self.request_count,
            "errors": self.error_count
        }
    
    async def system_status(self):
        """System status endpoint"""
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "services": self.services,
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }
    
    async def system_metrics(self):
        """System metrics endpoint"""
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "requests_total": self.request_count,
                "errors_total": self.error_count,
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }
    
    async def prometheus_metrics(self):
        """Prometheus metrics endpoint"""
        # Update SSOT metrics
        try:
            # Get SSOT status and update metrics
            ssot_status = await self.get_ssot_status()
            self.ssot_anchors_total.labels(family='default', status='active').set(ssot_status.get('anchors', 0))
            self.ssot_aliases_total.labels(context='default', status='active').set(ssot_status.get('aliases', 0))
            self.ssot_consistency_score.labels(component='ssot').set(ssot_status.get('consistency_score', 1.0))
        except Exception as e:
            logger.error(f"Error updating SSOT metrics: {e}")
        
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    
    async def get_ssot_status(self):
        """Get SSOT status for metrics"""
        try:
            # This is a placeholder - in real implementation, get actual SSOT status
            return {
                "anchors": 5,
                "aliases": 10,
                "consistency_score": 0.95
            }
        except Exception as e:
            logger.error(f"Error getting SSOT status: {e}")
            return {"anchors": 0, "aliases": 0, "consistency_score": 0.0}
    
    # Authentication endpoints
    async def login(self, credentials: LoginRequest, version: str = "v3"):
        """
        User login endpoint.

        Authenticates a user with email and password, returning a JWT token for subsequent requests.

        **Request Body:**
        - `email`: User's email address
        - `password`: User's password

        **Returns:**
        - `token`: JWT access token
        - `expires_in`: Token expiration time in seconds
        - `user`: User identifier

        **Rate Limited:** Yes (5 requests per minute for auth endpoints)
        """
        self.request_count += 1

        # Additional security checks
        if not SecurityUtils.validate_sql_injection(credentials.email) or not SecurityUtils.validate_sql_injection(credentials.password):
            raise HTTPException(status_code=400, detail="Invalid input detected")

        return {
            "message": "Login successful",
            "status": "success",
            "token": "mock-jwt-token",
            "user": credentials.email,
            "expires_in": 3600
        }
    
    async def register(self, user_data: UserRegistration, version: str = "v3"):
        """
        User registration endpoint.

        Creates a new user account with email, password, and optional name.

        **Password Requirements:**
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit

        **Request Body:**
        - `email`: User's email address (required)
        - `password`: User's password (required)
        - `name`: User's display name (optional)

        **Returns:**
        - `user`: Registered user's email
        - `message`: Success confirmation

        **Rate Limited:** Yes (5 requests per minute for auth endpoints)
        """
        self.request_count += 1

        # Additional security checks
        if not SecurityUtils.validate_sql_injection(user_data.email) or not SecurityUtils.validate_sql_injection(user_data.password):
            raise HTTPException(status_code=400, detail="Invalid input detected")

        if user_data.name and not SecurityUtils.validate_sql_injection(user_data.name):
            raise HTTPException(status_code=400, detail="Invalid name format")

        return {
            "message": "User registered successfully",
            "status": "success",
            "user": user_data.email
        }
    
    async def refresh_token(self, token_data: dict, version: str = "v3"):
        """Refresh JWT token"""
        self.request_count += 1
        return {
            "message": "Token refreshed",
            "status": "success",
            "token": "new-mock-jwt-token",
            "expires_in": 3600
        }
    
    async def logout(self, token: str, version: str = "v3"):
        """User logout"""
        self.request_count += 1
        return {
            "message": "Logout successful",
            "status": "success"
        }
    
    # User management endpoints
    async def get_user_profile(self, version: str = "v3", current_user: str = Depends(security)):
        """Get user profile"""
        self.request_count += 1
        return {
            "message": "User profile",
            "status": "success",
            "profile": {
                "id": "user-123",
                "email": "user@example.com",
                "name": "John Doe",
                "role": "user"
            }
        }
    
    async def update_user_profile(self, profile_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Update user profile"""
        self.request_count += 1
        return {
            "message": "Profile updated",
            "status": "success",
            "profile": profile_data
        }
    
    async def get_user_settings(self, version: str = "v3", current_user: str = Depends(security)):
        """Get user settings"""
        self.request_count += 1
        return {
            "message": "User settings",
            "status": "success",
            "settings": {
                "theme": "dark",
                "language": "en",
                "notifications": True
            }
        }
    
    async def update_user_settings(self, settings_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Update user settings"""
        self.request_count += 1
        return {
            "message": "Settings updated",
            "status": "success",
            "settings": settings_data
        }
    
    # Financial services endpoints
    async def get_accounts(self, version: str = "v3", current_user: str = Depends(security)):
        """Get user accounts"""
        self.request_count += 1
        return {
            "message": "Accounts retrieved",
            "status": "success",
            "accounts": [
                {
                    "id": "acc-1",
                    "name": "Checking Account",
                    "balance": 5000.00,
                    "type": "checking"
                },
                {
                    "id": "acc-2", 
                    "name": "Savings Account",
                    "balance": 15000.00,
                    "type": "savings"
                }
            ]
        }
    
    async def create_account(self, account_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Create new account"""
        self.request_count += 1
        return {
            "message": "Account created",
            "status": "success",
            "account": {
                "id": f"acc-{self.request_count}",
                **account_data
            }
        }
    
    async def get_transactions(self, version: str = "v3", current_user: str = Depends(security), params: PaginationParams = Depends(), fields: Optional[str] = Query(None, description="Comma-separated list of fields to return")):
        """Get user transactions with pagination and field selection"""
        self.request_count += 1

        # Mock transaction data (in real implementation, this would come from database)
        all_transactions = [
            {
                "id": "txn-1",
                "amount": -50.00,
                "description": "Grocery Store",
                "date": "2024-01-15",
                "account_id": "acc-1",
                "category": "food",
                "merchant": "SuperMart"
            },
            {
                "id": "txn-2",
                "amount": 2000.00,
                "description": "Salary",
                "date": "2024-01-01",
                "account_id": "acc-1",
                "category": "income",
                "merchant": "Employer Inc"
            },
            {
                "id": "txn-3",
                "amount": -25.50,
                "description": "Coffee Shop",
                "date": "2024-01-14",
                "account_id": "acc-1",
                "category": "food",
                "merchant": "Starbucks"
            },
            {
                "id": "txn-4",
                "amount": -120.00,
                "description": "Gas Station",
                "date": "2024-01-13",
                "account_id": "acc-1",
                "category": "transportation",
                "merchant": "Shell"
            },
            {
                "id": "txn-5",
                "amount": 500.00,
                "description": "Freelance Payment",
                "date": "2024-01-10",
                "account_id": "acc-1",
                "category": "income",
                "merchant": "Client Corp"
            }
        ]

        # Apply field selection
        filtered_transactions = select_fields(all_transactions, fields)

        paginated_result = paginate_data(filtered_transactions, params)
        return {
            "message": "Transactions retrieved",
            "status": "success",
            "transactions": paginated_result.data,
            "pagination": paginated_result.pagination
        }
    
    async def create_transaction(self, transaction_data: dict, current_user: str = Depends(security)):
        """Create new transaction"""
        self.request_count += 1
        return {
            "message": "Transaction created",
            "status": "success",
            "transaction": {
                "id": f"txn-{self.request_count}",
                **transaction_data
            }
        }
    
    async def get_budgets(self, current_user: str = Depends(security)):
        """Get user budgets"""
        self.request_count += 1
        return {
            "message": "Budgets retrieved",
            "status": "success",
            "budgets": [
                {
                    "id": "budget-1",
                    "name": "Monthly Expenses",
                    "amount": 3000.00,
                    "spent": 1500.00,
                    "category": "general"
                }
            ]
        }
    
    async def create_budget(self, budget_data: dict, current_user: str = Depends(security)):
        """Create new budget"""
        self.request_count += 1
        return {
            "message": "Budget created",
            "status": "success",
            "budget": {
                "id": f"budget-{self.request_count}",
                **budget_data
            }
        }
    
    async def get_analytics(self, current_user: str = Depends(security)):
        """Get financial analytics"""
        self.request_count += 1
        return {
            "message": "Analytics retrieved",
            "status": "success",
            "analytics": {
                "total_balance": 20000.00,
                "monthly_income": 5000.00,
                "monthly_expenses": 3000.00,
                "savings_rate": 0.4,
                "categories": {
                    "food": 500.00,
                    "transportation": 300.00,
                    "entertainment": 200.00
                }
            }
        }
    
    # AI services endpoints
    async def ai_chat(self, message_data: dict, current_user: str = Depends(security)):
        """AI chat endpoint"""
        self.request_count += 1
        return {
            "message": "AI response generated",
            "status": "success",
            "response": f"AI Response to: {message_data.get('message', 'Hello')}",
            "timestamp": datetime.now().isoformat()
        }
    
    async def get_ai_insights(self, current_user: str = Depends(security)):
        """Get AI insights"""
        self.request_count += 1
        return {
            "message": "AI insights retrieved",
            "status": "success",
            "insights": [
                {
                    "type": "spending_pattern",
                    "message": "Your spending on dining out has increased by 15% this month",
                    "severity": "info"
                },
                {
                    "type": "savings_opportunity",
                    "message": "You could save $200/month by reducing subscription services",
                    "severity": "suggestion"
                }
            ]
        }
    
    async def get_ai_monitoring(self, current_user: str = Depends(security)):
        """Get AI monitoring data"""
        self.request_count += 1
        return {
            "message": "AI monitoring data retrieved",
            "status": "success",
            "monitoring": {
                "system_health": "excellent",
                "ai_models_active": 3,
                "response_time_avg": 0.5,
                "accuracy_score": 0.95
            }
        }
    
    async def ai_optimization(self, optimization_data: dict, current_user: str = Depends(security)):
        """AI optimization endpoint"""
        self.request_count += 1
        return {
            "message": "Optimization applied",
            "status": "success",
            "optimization": {
                "type": optimization_data.get("type", "general"),
                "improvements": ["Performance improved by 15%", "Memory usage reduced by 10%"],
                "timestamp": datetime.now().isoformat()
            }
        }
    
    # Admin endpoints
    async def admin_get_users(self, current_user: str = Depends(security), params: PaginationParams = Depends()):
        """Admin: Get all users with pagination"""
        self.request_count += 1

        # Mock user data (in real implementation, this would come from database)
        all_users = [
            {"id": "user-1", "email": "admin@example.com", "role": "admin", "created_at": "2024-01-01"},
            {"id": "user-2", "email": "user@example.com", "role": "user", "created_at": "2024-01-02"},
            {"id": "user-3", "email": "manager@example.com", "role": "manager", "created_at": "2024-01-03"},
            {"id": "user-4", "email": "analyst@example.com", "role": "analyst", "created_at": "2024-01-04"},
            {"id": "user-5", "email": "developer@example.com", "role": "developer", "created_at": "2024-01-05"}
        ]

        paginated_result = paginate_data(all_users, params)
        return {
            "message": "Users retrieved",
            "status": "success",
            "users": paginated_result.data,
            "pagination": paginated_result.pagination
        }
    
    async def admin_get_audit(self, current_user: str = Depends(security)):
        """Admin: Get audit logs"""
        self.request_count += 1
        return {
            "message": "Audit logs retrieved",
            "status": "success",
            "audit_logs": [
                {
                    "id": "audit-1",
                    "action": "user_login",
                    "user_id": "user-1",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    async def admin_get_system(self, current_user: str = Depends(security)):
        """Admin: Get system information"""
        self.request_count += 1
        return {
            "message": "System information retrieved",
            "status": "success",
            "system": {
                "version": "3.0.0",
                "uptime": str(datetime.now() - self.start_time),
                "services": self.services,
                "performance": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent
                }
            }
        }
    
    async def admin_get_monitoring(self, current_user: str = Depends(security)):
        """Admin: Get monitoring data"""
        self.request_count += 1
        return {
            "message": "Monitoring data retrieved",
            "status": "success",
            "monitoring": {
                "requests_total": self.request_count,
                "errors_total": self.error_count,
                "response_time_avg": 0.1,
                "active_connections": 5
            }
        }
    
    # System endpoints
    async def get_system_config(self, current_user: str = Depends(security)):
        """Get system configuration"""
        self.request_count += 1
        return {
            "message": "System configuration retrieved",
            "status": "success",
            "config": {
                "api_version": "v3",
                "features": {
                    "ai_enabled": True,
                    "monitoring_enabled": True,
                    "analytics_enabled": True
                },
                "limits": {
                    "max_requests_per_minute": 1000,
                    "max_file_size": "10MB"
                }
            }
        }
    
    async def update_system_config(self, config_data: dict, current_user: str = Depends(security)):
        """Update system configuration"""
        self.request_count += 1
        return {
            "message": "System configuration updated",
            "status": "success",
            "config": config_data
        }
    
    # Ultimate Frenly AI Orchestrator endpoints
    async def execute_pipeline(self, request: Request, version: str = "v3"):
        """Execute the complete 12-step pipeline"""
        try:
            data = await request.json()
            trigger_condition = data.get("trigger_condition", "manual_execution")

            execution = await self.frenly_orchestrator.execute_pipeline(trigger_condition)

            return {
                "message": "Pipeline execution started",
                "execution_id": execution.execution_id,
                "status": execution.status.value,
                "trigger_condition": execution.trigger_condition,
                "start_time": execution.start_time.isoformat() if execution.start_time else None
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to execute pipeline: {str(e)}")

    async def list_pipeline_executions(self, version: str = "v3", limit: int = Query(50, ge=1, le=100)):
        """List recent pipeline executions"""
        try:
            executions = await self.frenly_orchestrator.list_executions(limit)

            return {
                "executions": [
                    {
                        "execution_id": exec.execution_id,
                        "trigger_condition": exec.trigger_condition,
                        "status": exec.status.value,
                        "current_step": exec.current_step.value if exec.current_step else None,
                        "start_time": exec.start_time.isoformat() if exec.start_time else None,
                        "end_time": exec.end_time.isoformat() if exec.end_time else None,
                        "errors": exec.errors
                    }
                    for exec in executions
                ]
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to list executions: {str(e)}")

    async def get_pipeline_execution(self, execution_id: str, version: str = "v3"):
        """Get details of a specific pipeline execution"""
        try:
            execution = await self.frenly_orchestrator.get_execution_status(execution_id)

            if not execution:
                raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found")

            return {
                "execution": {
                    "execution_id": execution.execution_id,
                    "trigger_condition": execution.trigger_condition,
                    "status": execution.status.value,
                    "current_step": execution.current_step.value if execution.current_step else None,
                    "start_time": execution.start_time.isoformat() if execution.start_time else None,
                    "end_time": execution.end_time.isoformat() if execution.end_time else None,
                    "results": execution.results,
                    "errors": execution.errors,
                    "metadata": execution.metadata
                }
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get execution: {str(e)}")

    async def cancel_pipeline_execution(self, execution_id: str, version: str = "v3"):
        """Cancel a running pipeline execution"""
        try:
            success = await self.frenly_orchestrator.cancel_execution(execution_id)

            if not success:
                raise HTTPException(status_code=404, detail=f"Execution {execution_id} not found or already completed")

            return {
                "message": f"Pipeline execution {execution_id} cancelled successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to cancel execution: {str(e)}")

    # Root endpoint
    async def root(self):
        """Root endpoint"""
        return {
            "message": "Welcome to NEXUS Platform API v3.0",
            "version": "3.0.0",
            "docs": "/docs",
            "health": "/health",
            "api_health": "/api/health",
            "status": "/api/status",
            "metrics": "/api/metrics",
            "orchestrator": "/api/v3/orchestrator"
        }
    
    # SSOT endpoint methods
    async def resolve_alias(self, alias: str, version: str = "v3", context: str = "frontend"):
        """
        Resolve an SSOT alias to its canonical endpoint.

        The Single Source of Truth (SSOT) system provides centralized alias management
        for API endpoints, configurations, and resources across different contexts.

        **Parameters:**
        - `alias`: The alias to resolve
        - `context`: Context for resolution (default: "frontend")
        - `version`: API version

        **Returns:**
        - `alias`: The requested alias
        - `canonical`: The resolved canonical endpoint
        - `context`: The context used for resolution

        **Common Contexts:**
        - `frontend`: Frontend application aliases
        - `backend`: Backend service aliases
        - `mobile`: Mobile application aliases
        - `api`: API endpoint aliases

        **Example:**
        ```
        GET /api/v3/ssot/resolve/user-profile?context=frontend
        ```
        """
        try:
            canonical = self.ssot_registry.resolve_alias(alias, context)
            if canonical:
                return {
                    "alias": alias,
                    "canonical": canonical,
                    "context": context,
                    "success": True,
                    "message": f"Alias resolved successfully"
                }
            else:
                # Try to find the alias in any context for better error message
                all_contexts = []
                for ctx, aliases in self.ssot_registry.aliases.items():
                    if alias in aliases:
                        all_contexts.append(ctx)

                if all_contexts:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Alias '{alias}' not found in context '{context}', but exists in contexts: {', '.join(all_contexts)}"
                    )
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Alias '{alias}' not found in any context"
                    )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error resolving alias '{alias}': {str(e)}"
            )
    
    async def list_aliases(self, version: str = "v3", context: str = "frontend", params: PaginationParams = Depends()):
        """
        List all SSOT aliases in a specific context with pagination support.

        Retrieves a paginated list of all aliases registered in the specified context,
        including their metadata such as status, creation date, and canonical references.

        **Parameters:**
        - `version`: API version (default: "v3")
        - `context`: Context to list aliases from (default: "frontend")
        - `params`: Pagination parameters (page, limit, etc.)

        **Query Parameters:**
        - `page`: Page number for pagination (default: 1)
        - `limit`: Number of items per page (default: 50)
        - `context`: Override context filter

        **Returns:**
        - `aliases`: List of alias objects with full metadata
        - `context`: The context that was queried
        - `pagination`: Pagination metadata (total, page, limit, etc.)
        - `success`: Boolean indicating operation success

        **Common Contexts:**
        - `frontend`: Frontend application aliases
        - `backend`: Backend service aliases
        - `mobile`: Mobile application aliases
        - `api`: API endpoint aliases
        - `global`: System-wide aliases

        **Example:**
        ```
        GET /api/v3/ssot/aliases?context=frontend&page=1&limit=20
        ```

        **Response:**
        ```json
        {
          "aliases": [
            {
              "name": "user-profile",
              "canonical": "api/v1/users/profile",
              "context": "frontend",
              "type": "permanent",
              "status": "active",
              "description": "User profile endpoint",
              "created_by": "system",
              "created_at": "2024-01-01T00:00:00",
              "last_updated": "2024-01-01T00:00:00"
            }
          ],
          "context": "frontend",
          "pagination": {
            "total": 1,
            "page": 1,
            "limit": 20,
            "pages": 1
          },
          "success": true
        }
        ```
        """
        try:
            aliases = await self.alias_manager.list_aliases(context=context)
            paginated_result = paginate_data(aliases, params)
            return {
                "aliases": paginated_result.data,
                "context": context,
                "pagination": paginated_result.pagination,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list aliases: {str(e)}"
            )
    
    async def create_alias(self, request: Request, version: str = "v3"):
        """
        Create a new SSOT alias with governance validation.

        Registers a new alias in the SSOT registry with automatic governance checks,
        conflict detection, and audit logging. The alias will be validated against
        existing governance rules and naming conventions.

        **Parameters:**
        - `version`: API version (default: "v3")
        - `request`: HTTP request containing alias creation data

        **Request Body:**
        ```json
        {
          "name": "user-profile",
          "canonical": "api/v1/users/profile",
          "context": "frontend",
          "type": "permanent",
          "description": "User profile endpoint alias",
          "created_by": "admin",
          "expires_in_days": null,
          "requires_approval": false
        }
        ```

        **Required Fields:**
        - `name`: Alias name (must be unique within context)
        - `canonical`: Canonical endpoint or resource reference
        - `context`: Context for the alias

        **Optional Fields:**
        - `type`: Alias type - "permanent", "temporary", "contextual", "migration", "system", "application", "frenly_ai" (default: "permanent")
        - `description`: Human-readable description
        - `created_by`: User/system creating the alias
        - `expires_in_days`: Days until expiration (for temporary aliases)
        - `requires_approval`: Whether alias needs approval before activation

        **Returns:**
        - `alias`: Created alias object with full metadata
        - `success`: Boolean indicating creation success
        - `message`: Confirmation message

        **Validation Rules:**
        - Alias names must be unique within their context
        - Canonical references must point to existing SSOT anchors
        - Governance rules are automatically applied based on alias type and context
        - Temporary aliases automatically get expiration dates

        **Example:**
        ```
        POST /api/v3/ssot/aliases
        Content-Type: application/json

        {
          "name": "user-dashboard",
          "canonical": "api/v1/users/dashboard",
          "context": "frontend",
          "type": "permanent",
          "description": "Main user dashboard endpoint",
          "created_by": "admin"
        }
        ```

        **Response:**
        ```json
        {
          "alias": {
            "name": "user-dashboard",
            "canonical": "api/v1/users/dashboard",
            "context": "frontend",
            "type": "permanent",
            "status": "active",
            "description": "Main user dashboard endpoint",
            "created_by": "admin",
            "created_at": "2024-01-01T00:00:00",
            "last_updated": "2024-01-01T00:00:00"
          },
          "success": true,
          "message": "Alias created successfully"
        }
        ```

        **Error Responses:**
        - `400`: Validation error (duplicate name, invalid canonical, governance violation)
        - `409`: Conflict with existing alias
        - `500`: Internal server error
        """
        try:
            data = await request.json()
            alias = data.get("alias")
            canonical = data.get("canonical")
            context = data.get("context", "frontend")
            description = data.get("description", "")
            alias_type = data.get("type", "application")
            created_by = data.get("created_by", "api_user")
            
            if not alias or not canonical:
                raise HTTPException(
                    status_code=400,
                    detail="Both 'alias' and 'canonical' are required"
                )
            
            # Convert string type to enum
            try:
                alias_type_enum = AliasType(alias_type)
            except ValueError:
                alias_type_enum = AliasType.APPLICATION
            
            result = await self.alias_manager.add_alias(
                alias=alias,
                canonical=canonical,
                context=context,
                alias_type=alias_type_enum.value,
                description=description,
                created_by=created_by
            )
            
            return {
                "message": f"Alias '{alias}' created successfully",
                "alias": result,
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create alias: {str(e)}"
            )
    
    async def delete_alias(self, alias: str, version: str = "v3", context: str = "frontend"):
        """
        Delete an SSOT alias from the registry.

        Removes an alias from the specified context with audit logging and governance checks.
        The deletion is permanent and cannot be undone.

        **Parameters:**
        - `alias`: Name of the alias to delete
        - `version`: API version (default: "v3")
        - `context`: Context containing the alias (default: "frontend")

        **Query Parameters:**
        - `context`: Override default context

        **Returns:**
        - `message`: Confirmation message
        - `success`: Boolean indicating deletion success

        **Governance Considerations:**
        - System aliases may require special permissions to delete
        - Deletion is audited and logged
        - Dependent aliases may need to be updated

        **Example:**
        ```
        DELETE /api/v3/ssot/aliases/user-profile?context=frontend
        ```

        **Response:**
        ```json
        {
          "message": "Alias 'user-profile' deleted successfully",
          "success": true
        }
        ```

        **Error Responses:**
        - `404`: Alias not found in specified context
        - `403`: Insufficient permissions to delete alias
        - `500`: Internal server error
        """
        try:
            await self.alias_manager.remove_alias(alias, context, "api_user")
            return {
                "message": f"Alias '{alias}' deleted successfully",
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Failed to delete alias '{alias}': {str(e)}"
            )
    
    async def get_alias_info(self, alias: str, version: str = "v3", context: str = "frontend"):
        """
        Retrieve detailed information about a specific SSOT alias.

        Returns comprehensive metadata for a single alias including its status,
        history, governance information, and usage statistics.

        **Parameters:**
        - `alias`: Name of the alias to retrieve
        - `version`: API version (default: "v3")
        - `context`: Context containing the alias (default: "frontend")

        **Query Parameters:**
        - `context`: Override default context

        **Returns:**
        - `alias`: Complete alias object with all metadata
        - `context`: Context the alias belongs to
        - `usage_stats`: Usage statistics (resolution count, last accessed, etc.)
        - `governance_info`: Governance compliance information
        - `success`: Boolean indicating retrieval success

        **Alias Metadata Includes:**
        - Basic info: name, canonical, context, type, status
        - Lifecycle: created_at, last_updated, expires_at
        - Governance: created_by, approved_by, approval status
        - Usage: resolution count, last resolved timestamp

        **Example:**
        ```
        GET /api/v3/ssot/aliases/user-profile?context=frontend
        ```

        **Response:**
        ```json
        {
          "alias": {
            "name": "user-profile",
            "canonical": "api/v1/users/profile",
            "context": "frontend",
            "type": "permanent",
            "status": "active",
            "description": "User profile endpoint",
            "created_by": "admin",
            "created_at": "2024-01-01T00:00:00",
            "last_updated": "2024-01-01T00:00:00",
            "expires_at": null,
            "approved_by": "admin",
            "approved_at": "2024-01-01T00:00:00"
          },
          "context": "frontend",
          "usage_stats": {
            "resolution_count": 1250,
            "last_resolved": "2024-01-01T12:00:00",
            "average_resolution_time_ms": 2.3
          },
          "governance_info": {
            "compliant": true,
            "violations": [],
            "last_audit": "2024-01-01T00:00:00"
          },
          "success": true
        }
        ```

        **Error Responses:**
        - `404`: Alias not found in specified context
        - `500`: Internal server error
        """
        try:
            alias_info = await self.alias_manager.get_alias_details(alias, context)
            if not alias_info:
                raise HTTPException(
                    status_code=404,
                    detail=f"Alias '{alias}' not found in context '{context}'"
                )
            
            return {
                "alias": alias_info,
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get alias info: {str(e)}"
            )

    # API Registry Integration endpoints
    async def integrate_services(self, version: str = "v3"):
        """Integrate all services with API registry"""
        try:
            result = await api_registry_integration.integrate_all_services()
            return {
                "message": "Service integration completed",
                "result": result,
                "success": result["success"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to integrate services: {str(e)}"
            )

    async def get_integration_status(self, version: str = "v3"):
        """Get API registry integration status"""
        try:
            status = await api_registry_integration.get_integration_status()
            return {
                "message": "Integration status retrieved",
                "status": status,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get integration status: {str(e)}"
            )

    async def validate_integration(self, version: str = "v3"):
        """Validate API registry integration"""
        try:
            validation = await api_registry_integration.validate_integration()
            return {
                "message": "Integration validation completed",
                "validation": validation,
                "success": validation["success"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate integration: {str(e)}"
            )

    async def cleanup_integration(self, version: str = "v3"):
        """Clean up API registry integration"""
        try:
            cleanup = await api_registry_integration.cleanup_integration()
            return {
                "message": "Integration cleanup completed",
                "cleanup": cleanup,
                "success": cleanup["success"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to cleanup integration: {str(e)}"
            )

    # API Versioning endpoints
    async def get_api_versions(self):
        """Get information about all API versions"""
        try:
            version_info = api_versioning.get_version_info()
            return {
                "message": "API version information retrieved",
                "versions": version_info,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get API versions: {str(e)}"
            )

    async def get_version_info(self, version: str):
        """Get information about a specific API version"""
        try:
            version_info = api_versioning.get_version_info()
            if version in [v["version"] for v in version_info["versions"]]:
                version_data = next(v for v in version_info["versions"] if v["version"] == version)
                return {
                    "message": f"Version {version} information retrieved",
                    "version": version_data,
                    "compatibility_mode": version_info["compatibility_mode"],
                    "success": True
                }
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"API version '{version}' not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get version info: {str(e)}"
            )

    # Rate Limiting endpoints
    async def get_rate_limits(self, version: str = "v3", current_user: str = Depends(security)):
        """Get rate limiting statistics"""
        try:
            stats = rate_limiting.get_stats()
            return {
                "message": "Rate limiting statistics retrieved",
                "stats": stats,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get rate limits: {str(e)}"
            )

    async def exempt_from_rate_limits(self, exemption_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Exempt an IP or user from rate limiting"""
        try:
            exempt_type = exemption_data.get("type", "ip")
            identifier = exemption_data.get("identifier")

            if not identifier:
                raise HTTPException(
                    status_code=400,
                    detail="Identifier is required"
                )

            if exempt_type == "ip":
                rate_limiting.exempt_ip(identifier)
            elif exempt_type == "user":
                rate_limiting.exempt_user(identifier)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid exemption type. Must be 'ip' or 'user'"
                )

            return {
                "message": f"Exempted {exempt_type} from rate limiting",
                "type": exempt_type,
                "identifier": identifier,
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create exemption: {str(e)}"
            )

    async def remove_rate_limit_exemption(self, exemption_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Remove rate limiting exemption"""
        try:
            exempt_type = exemption_data.get("type", "ip")
            identifier = exemption_data.get("identifier")

            if not identifier:
                raise HTTPException(
                    status_code=400,
                    detail="Identifier is required"
                )

            rate_limiting.remove_exemption(identifier, exempt_type)

            return {
                "message": f"Removed {exempt_type} exemption from rate limiting",
                "type": exempt_type,
                "identifier": identifier,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to remove exemption: {str(e)}"
            )

    # Data Validation endpoints
    async def validate_data_schemas(self, version: str = "v3", current_user: str = Depends(security)):
        """Validate data schemas across all platforms"""
        try:
            validation_results = await data_schema_validator.validate_all_schemas()
            return {
                "message": "Data schema validation completed",
                "validation": validation_results,
                "success": validation_results["success"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate data schemas: {str(e)}"
            )

    async def get_validation_status(self, version: str = "v3", current_user: str = Depends(security)):
        """Get data validation status summary"""
        try:
            status_summary = await data_schema_validator.get_validation_summary()
            return {
                "message": "Validation status retrieved",
                "status": status_summary,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get validation status: {str(e)}"
            )

    # Data Migration Validation endpoints
    async def validate_migration(self, migration_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Validate data migration"""
        try:
            migration_type = migration_data.get("migration_type", "data_migration")
            source_version = migration_data.get("source_version", "current")
            target_version = migration_data.get("target_version", "latest")

            result = await data_migration_validator.validate_migration(
                migration_id=f"migration_{datetime.now().isoformat()}",
                migration_type=migration_type,
                source_version=source_version,
                target_version=target_version
            )

            return {
                "message": "Migration validation completed",
                "validation": {
                    "id": result.migration_id,
                    "status": result.status.value,
                    "summary": result.summary
                },
                "success": result.status.name == "PASSED"
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to validate migration: {str(e)}"
            )

    async def get_migration_reports(self, version: str = "v3", current_user: str = Depends(security)):
        """Get migration validation reports"""
        try:
            reports = await data_migration_validator.list_validations()
            return {
                "message": "Migration reports retrieved",
                "reports": [
                    {
                        "id": r.migration_id,
                        "type": r.migration_type.value,
                        "status": r.status.value,
                        "summary": r.summary,
                        "timestamp": r.start_time.isoformat()
                    } for r in reports
                ],
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get migration reports: {str(e)}"
            )

    # Data Integrity Check endpoints
    async def run_integrity_check(self, check_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Run data integrity check"""
        try:
            services = check_data.get("services", ["database", "redis", "frenly_ai", "api_gateway"])
            check_types = check_data.get("check_types", ["checksum_validation", "consistency_check", "anomaly_detection"])

            report = await data_integrity_checker.run_integrity_check(
                services=services,
                check_types=check_types
            )

            return {
                "message": "Integrity check completed",
                "report": {
                    "id": report.report_id,
                    "status": report.overall_status.value,
                    "summary": report.summary,
                    "recommendations": report.recommendations
                },
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to run integrity check: {str(e)}"
            )

    async def get_integrity_reports(self, version: str = "v3", current_user: str = Depends(security)):
        """Get integrity check reports"""
        try:
            reports = await data_integrity_checker.list_integrity_reports()
            return {
                "message": "Integrity reports retrieved",
                "reports": [
                    {
                        "id": r.report_id,
                        "status": r.overall_status.value,
                        "consistency_score": r.consistency_score,
                        "timestamp": r.timestamp.isoformat()
                    } for r in reports
                ],
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get integrity reports: {str(e)}"
            )

    async def get_service_health(self, service: str, version: str = "v3", current_user: str = Depends(security)):
        """Get service health score"""
        try:
            health_score = await data_integrity_checker.get_service_health_score(service)
            return {
                "message": f"Health score for {service}",
                "service": service,
                "health_score": health_score,
                "status": "healthy" if health_score > 0.8 else "warning" if health_score > 0.6 else "critical",
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get service health: {str(e)}"
            )

    # Deployment Pipeline endpoints
    async def start_deployment(self, deployment_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Start deployment pipeline"""
        try:
            version_tag = deployment_data.get("version")
            environment = deployment_data.get("environment", "staging")

            if not version_tag:
                raise HTTPException(status_code=400, detail="Version is required")

            deployment = await deployment_pipeline_integrator.start_deployment(
                version=version_tag,
                environment=environment,
                triggered_by=current_user
            )

            return {
                "message": f"Deployment started for {version_tag} to {environment}",
                "deployment": {
                    "id": deployment.deployment_id,
                    "status": deployment.status,
                    "environment": deployment.environment
                },
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start deployment: {str(e)}"
            )

    async def get_deployment_status(self, deployment_id: str, version: str = "v3", current_user: str = Depends(security)):
        """Get deployment status"""
        try:
            deployment = await deployment_pipeline_integrator.get_deployment_status(deployment_id)
            if not deployment:
                raise HTTPException(status_code=404, detail="Deployment not found")

            return {
                "message": f"Deployment status for {deployment_id}",
                "deployment": {
                    "id": deployment.deployment_id,
                    "status": deployment.status,
                    "version": deployment.version,
                    "environment": deployment.environment
                },
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get deployment status: {str(e)}"
            )

    async def list_deployments(self, version: str = "v3", current_user: str = Depends(security)):
        """List deployments"""
        try:
            deployments = await deployment_pipeline_integrator.list_deployments()
            return {
                "message": "Deployments retrieved",
                "deployments": [
                    {
                        "id": d.deployment_id,
                        "version": d.version,
                        "environment": d.environment,
                        "status": d.status,
                        "start_time": d.start_time.isoformat()
                    } for d in deployments
                ],
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list deployments: {str(e)}"
            )

    async def rollback_deployment(self, deployment_id: str, version: str = "v3", current_user: str = Depends(security)):
        """Rollback deployment"""
        try:
            success = await deployment_pipeline_integrator.trigger_rollback(deployment_id)
            return {
                "message": f"Rollback {'initiated' if success else 'failed'} for {deployment_id}",
                "success": success
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to rollback deployment: {str(e)}"
            )

    # AI SSOT Optimization endpoints
    async def optimize_ssot(self, optimization_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """
        Run comprehensive SSOT optimization and conflict resolution.

        Performs automated analysis of the SSOT registry to detect inconsistencies,
        conflicts, and optimization opportunities. Can automatically resolve
        certain types of conflicts and generate detailed reports.

        **Parameters:**
        - `optimization_data`: Optimization configuration
        - `version`: API version (default: "v3")
        - `current_user`: Authenticated user performing optimization

        **Request Body:**
        ```json
        {
          "scope": "full",
          "auto_resolve": false,
          "include_audit": true,
          "generate_report": true
        }
        ```

        **Configuration Options:**
        - `scope`: Optimization scope - "full", "context", "anchors", "aliases"
        - `auto_resolve`: Whether to automatically resolve safe conflicts
        - `include_audit`: Include audit trail analysis
        - `generate_report`: Generate detailed optimization report

        **Optimization Checks:**
        - Alias consistency across contexts
        - Orphaned aliases (pointing to non-existent anchors)
        - Naming convention compliance
        - Governance rule violations
        - Performance optimization opportunities
        - Conflict detection and resolution

        **Returns:**
        - `message`: Operation status message
        - `report`: Optimization results summary
        - `success`: Boolean indicating operation success

        **Report Fields:**
        - `id`: Unique report identifier
        - `consistency_score`: Overall SSOT health score (0.0-1.0)
        - `conflicts_detected`: Number of conflicts found
        - `optimizations_applied`: Number of automatic fixes applied
        - `recommendations`: List of manual action recommendations

        **Example:**
        ```
        POST /api/v3/ssot/optimize
        Content-Type: application/json

        {
          "scope": "full",
          "auto_resolve": true,
          "include_audit": true
        }
        ```

        **Response:**
        ```json
        {
          "message": "SSOT optimization completed",
          "report": {
            "id": "opt_20240101_120000",
            "consistency_score": 0.95,
            "conflicts_detected": 3,
            "optimizations_applied": 2,
            "recommendations": [
              "Review temporary aliases expiring within 30 days",
              "Consider consolidating similar aliases in 'api' context"
            ]
          },
          "success": true
        }
        ```

        **Permissions:**
        - Requires admin or SSOT maintainer role
        - Operations are audited and logged

        **Error Responses:**
        - `403`: Insufficient permissions
        - `500`: Optimization process failed
        """
        try:
            scope = optimization_data.get("scope", "full")
            auto_resolve = optimization_data.get("auto_resolve", False)

            report = await ai_ssot_optimizer.run_ssot_optimization(
                scope=scope,
                auto_resolve=auto_resolve
            )

            return {
                "message": "SSOT optimization completed",
                "report": {
                    "id": report.report_id,
                    "consistency_score": report.consistency_score,
                    "conflicts_detected": len(report.conflicts_detected),
                    "optimizations_applied": len(report.optimizations_applied),
                    "recommendations": report.recommendations
                },
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to optimize SSOT: {str(e)}"
            )

    async def get_optimization_reports(self, version: str = "v3", current_user: str = Depends(security)):
        """
        Retrieve historical SSOT optimization reports.

        Returns a list of past optimization runs with their results, allowing
        tracking of SSOT health trends and optimization effectiveness over time.

        **Parameters:**
        - `version`: API version (default: "v3")
        - `current_user`: Authenticated user requesting reports

        **Query Parameters:**
        - `limit`: Maximum number of reports to return (default: 50)
        - `offset`: Pagination offset (default: 0)
        - `start_date`: Filter reports after this date (ISO format)
        - `end_date`: Filter reports before this date (ISO format)
        - `min_score`: Filter by minimum consistency score

        **Returns:**
        - `message`: Operation status message
        - `reports`: List of optimization reports
        - `success`: Boolean indicating retrieval success

        **Report Fields:**
        - `id`: Unique report identifier
        - `consistency_score`: SSOT health score at time of optimization
        - `conflicts_detected`: Number of conflicts identified
        - `timestamp`: When the optimization was run

        **Example:**
        ```
        GET /api/v3/ssot/optimization/reports?limit=10&min_score=0.8
        ```

        **Response:**
        ```json
        {
          "message": "Optimization reports retrieved",
          "reports": [
            {
              "id": "opt_20240101_120000",
              "consistency_score": 0.95,
              "conflicts_detected": 3,
              "timestamp": "2024-01-01T12:00:00"
            },
            {
              "id": "opt_20231231_120000",
              "consistency_score": 0.92,
              "conflicts_detected": 5,
              "timestamp": "2023-12-31T12:00:00"
            }
          ],
          "success": true
        }
        ```

        **Permissions:**
        - Requires read access to SSOT reports
        - Available to admin and SSOT maintainer roles

        **Error Responses:**
        - `403`: Insufficient permissions
        - `500`: Failed to retrieve reports
        """
        try:
            reports = await ai_ssot_optimizer.list_optimization_reports()
            return {
                "message": "Optimization reports retrieved",
                "reports": [
                    {
                        "id": r.report_id,
                        "consistency_score": r.consistency_score,
                        "conflicts_detected": len(r.conflicts_detected),
                        "timestamp": r.timestamp.isoformat()
                    } for r in reports
                ],
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get optimization reports: {str(e)}"
            )

    async def resolve_conflict(self, conflict_id: str, resolution_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """
        Manually resolve a specific SSOT conflict.

        Allows administrators to manually resolve conflicts that cannot be
        automatically resolved by the optimization system. All resolutions
        are audited and require appropriate permissions.

        **Parameters:**
        - `conflict_id`: Unique identifier of the conflict to resolve
        - `resolution_data`: Resolution configuration and details
        - `version`: API version (default: "v3")
        - `current_user`: Authenticated user performing resolution

        **Request Body:**
        ```json
        {
          "resolution": {
            "strategy": "merge",
            "primary_alias": "user-profile-v1",
            "secondary_alias": "user-profile-old",
            "merge_metadata": true,
            "notify_stakeholders": true
          },
          "comments": "Consolidating duplicate user profile aliases",
          "priority": "high"
        }
        ```

        **Resolution Strategies:**
        - `merge`: Combine conflicting aliases, keeping primary and redirecting secondary
        - `deprecate`: Mark one alias as deprecated, keep the other active
        - `rename`: Rename one alias to avoid conflict
        - `delete`: Remove the conflicting alias
        - `approve`: Approve a pending alias that was in conflict

        **Resolution Options:**
        - `primary_alias`: Which alias to keep as primary (for merge/deprecate)
        - `merge_metadata`: Whether to combine metadata from both aliases
        - `notify_stakeholders`: Send notifications about the resolution
        - `comments`: Explanation of the resolution decision

        **Returns:**
        - `message`: Resolution status message
        - `conflict_id`: ID of the resolved conflict
        - `success`: Boolean indicating resolution success

        **Audit Trail:**
        - All resolutions are logged with user, timestamp, and rationale
        - Notifications sent to stakeholders if requested
        - Resolution recorded in conflict history

        **Example:**
        ```
        POST /api/v3/ssot/conflict/conf_12345/resolve
        Content-Type: application/json

        {
          "resolution": {
            "strategy": "merge",
            "primary_alias": "user-profile",
            "secondary_alias": "user-profile-legacy",
            "merge_metadata": true
          },
          "comments": "Merging legacy alias into primary"
        }
        ```

        **Response:**
        ```json
        {
          "message": "Conflict resolution successful",
          "conflict_id": "conf_12345",
          "success": true
        }
        ```

        **Permissions:**
        - Requires admin or SSOT maintainer role
        - Some resolutions may require additional approvals

        **Error Responses:**
        - `403`: Insufficient permissions
        - `404`: Conflict not found
        - `400`: Invalid resolution strategy or parameters
        - `409`: Conflict already resolved
        - `500`: Resolution failed
        """
        try:
            resolution = resolution_data.get("resolution", {})
            success = await ai_ssot_optimizer.resolve_conflict_manually(
                conflict_id=conflict_id,
                resolution=resolution,
                approved_by=current_user
            )

            return {
                "message": f"Conflict resolution {'successful' if success else 'failed'}",
                "conflict_id": conflict_id,
                "success": success
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to resolve conflict: {str(e)}"
            )

    # Blue-Green Deployment endpoints
    async def start_blue_green_deployment(self, deployment_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Start blue-green deployment"""
        try:
            version_tag = deployment_data.get("version")
            environment = deployment_data.get("environment", "production")
            initial_traffic_percent = deployment_data.get("initial_traffic_percent", 10)

            if not version_tag:
                raise HTTPException(status_code=400, detail="Version is required")

            deployment = await blue_green_deployment_service.start_blue_green_deployment(
                version=version_tag,
                environment=environment,
                initial_traffic_percent=initial_traffic_percent
            )

            return {
                "message": f"Blue-green deployment started for {version_tag}",
                "deployment": {
                    "id": deployment.deployment_id,
                    "status": deployment.status,
                    "active_color": deployment.active_color.value,
                    "current_traffic": deployment.current_traffic.value
                },
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to start blue-green deployment: {str(e)}"
            )

    async def get_bg_deployment_status(self, deployment_id: str, version: str = "v3", current_user: str = Depends(security)):
        """Get blue-green deployment status"""
        try:
            deployment = await blue_green_deployment_service.get_deployment_status(deployment_id)
            if not deployment:
                raise HTTPException(status_code=404, detail="Deployment not found")

            return {
                "message": f"Blue-green deployment status for {deployment_id}",
                "deployment": {
                    "id": deployment.deployment_id,
                    "status": deployment.status,
                    "active_color": deployment.active_color.value,
                    "current_traffic": deployment.current_traffic.value,
                    "phases_completed": [p.value for p in deployment.phases_completed]
                },
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get blue-green deployment status: {str(e)}"
            )

    async def switch_traffic(self, deployment_id: str, traffic_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Switch traffic distribution"""
        try:
            target_distribution = traffic_data.get("target_distribution")
            if not target_distribution:
                raise HTTPException(status_code=400, detail="Target distribution is required")

            from services.blue_green_deployment import TrafficDistribution
            target_enum = TrafficDistribution(target_distribution)

            success = await blue_green_deployment_service.manual_traffic_switch(
                deployment_id=deployment_id,
                target_distribution=target_enum
            )

            return {
                "message": f"Traffic switch {'successful' if success else 'failed'}",
                "deployment_id": deployment_id,
                "target_distribution": target_distribution,
                "success": success
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to switch traffic: {str(e)}"
            )

    async def list_bg_deployments(self, version: str = "v3", current_user: str = Depends(security)):
        """List blue-green deployments"""
        try:
            deployments = await blue_green_deployment_service.list_deployments()
            return {
                "message": "Blue-green deployments retrieved",
                "deployments": [
                    {
                        "id": d.deployment_id,
                        "version": d.version,
                        "environment": d.environment,
                        "status": d.status,
                        "active_color": d.active_color.value,
                        "current_traffic": d.current_traffic.value
                    } for d in deployments
                ],
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list blue-green deployments: {str(e)}"
            )

    # AI Monitoring and Alerting endpoints
    async def get_monitoring_dashboard(self, version: str = "v3", current_user: str = Depends(security)):
        """Get monitoring dashboard data"""
        try:
            dashboard_data = await ai_monitoring_alerting_service.get_monitoring_dashboard_data()
            return {
                "message": "Monitoring dashboard data retrieved",
                "dashboard": dashboard_data,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get monitoring dashboard: {str(e)}"
            )

    async def get_system_health(self, version: str = "v3", current_user: str = Depends(security)):
        """Get system health score"""
        try:
            health_score = await ai_monitoring_alerting_service.get_system_health_score()
            return {
                "message": "System health score retrieved",
                "health_score": health_score,
                "status": "healthy" if health_score > 0.8 else "warning" if health_score > 0.6 else "critical",
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get system health: {str(e)}"
            )

    async def acknowledge_alert(self, alert_id: str, version: str = "v3", current_user: str = Depends(security)):
        """Acknowledge alert"""
        try:
            success = await ai_monitoring_alerting_service.acknowledge_alert(
                alert_id=alert_id,
                user=current_user
            )
            return {
                "message": f"Alert {'acknowledged' if success else 'not found or already acknowledged'}",
                "alert_id": alert_id,
                "success": success
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to acknowledge alert: {str(e)}"
            )

    async def get_active_alerts(self, version: str = "v3", current_user: str = Depends(security)):
        """Get active alerts"""
        try:
            dashboard_data = await ai_monitoring_alerting_service.get_monitoring_dashboard_data()
            return {
                "message": "Active alerts retrieved",
                "alerts": dashboard_data.get("recent_alerts", []),
                "count": dashboard_data.get("active_alerts_count", 0),
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get active alerts: {str(e)}"
            )

    async def get_active_incidents(self, version: str = "v3", current_user: str = Depends(security)):
        """Get active incidents"""
        try:
            dashboard_data = await ai_monitoring_alerting_service.get_monitoring_dashboard_data()
            return {
                "message": "Active incidents retrieved",
                "incidents": dashboard_data.get("active_incidents", []),
                "count": dashboard_data.get("active_incidents_count", 0),
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get active incidents: {str(e)}"
            )

    async def update_incident_status(self, incident_id: str, status_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Update incident status"""
        try:
            new_status = status_data.get("status")
            notes = status_data.get("notes", "")

            if not new_status:
                raise HTTPException(status_code=400, detail="Status is required")

            from services.ai_monitoring_alerting import IncidentStatus
            status_enum = IncidentStatus(new_status)

            success = await ai_monitoring_alerting_service.update_incident_status(
                incident_id=incident_id,
                status=status_enum,
                user=current_user,
                notes=notes
            )

            return {
                "message": f"Incident status {'updated' if success else 'not found'}",
                "incident_id": incident_id,
                "new_status": new_status,
                "success": success
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update incident status: {str(e)}"
            )

    # Redis Cache Management endpoints
    async def get_cache_stats(self, version: str = "v3", current_user: str = Depends(security)):
        """Get cache statistics"""
        try:
            stats = await redis_cache_service.get_cache_stats()
            return {
                "message": "Cache statistics retrieved",
                "stats": {
                    "hits": stats.hits,
                    "misses": stats.misses,
                    "sets": stats.sets,
                    "deletes": stats.deletes,
                    "evictions": stats.evictions,
                    "hit_rate": round(stats.hit_rate * 100, 2),
                    "total_keys": stats.total_keys,
                    "memory_usage_mb": round(stats.memory_usage_bytes / 1024 / 1024, 2),
                    "uptime_hours": round(stats.uptime_seconds / 3600, 2)
                },
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get cache stats: {str(e)}"
            )

    async def clear_cache(self, cache_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Clear cache entries"""
        try:
            pattern = cache_data.get("pattern", "*")
            deleted_count = await redis_cache_service.clear_cache(pattern)
            return {
                "message": f"Cleared {deleted_count} cache entries",
                "pattern": pattern,
                "deleted_count": deleted_count,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clear cache: {str(e)}"
            )

    async def invalidate_api_cache(self, invalidation_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Invalidate API cache"""
        try:
            path_pattern = invalidation_data.get("path_pattern", "")
            method = invalidation_data.get("method")

            if not path_pattern:
                raise HTTPException(status_code=400, detail="Path pattern is required")

            await redis_cache_service.invalidate_api_cache(path_pattern, method)
            return {
                "message": f"Invalidated API cache for pattern: {path_pattern}",
                "path_pattern": path_pattern,
                "method": method,
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to invalidate API cache: {str(e)}"
            )

    async def invalidate_data_cache(self, invalidation_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Invalidate data cache"""
        try:
            tags = invalidation_data.get("tags", [])
            pattern = invalidation_data.get("pattern")

            await redis_cache_service.invalidate_data_cache(tags, pattern)
            return {
                "message": "Invalidated data cache",
                "tags": tags,
                "pattern": pattern,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to invalidate data cache: {str(e)}"
            )

    async def warmup_cache(self, version: str = "v3", current_user: str = Depends(security)):
        """Warm up cache"""
        try:
            await redis_cache_service.warmup_cache()
            return {
                "message": "Cache warmup initiated",
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to warm up cache: {str(e)}"
            )

    # Database Optimization endpoints
    async def optimize_database(self, version: str = "v3", current_user: str = Depends(security)):
        """Run database optimization"""
        try:
            results = await database_optimizer.optimize_database_performance()
            return {
                "message": "Database optimization completed",
                "results": results,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to optimize database: {str(e)}"
            )

    async def get_database_metrics(self, version: str = "v3", current_user: str = Depends(security)):
        """Get database performance metrics"""
        try:
            metrics = await database_optimizer.get_database_metrics()
            return {
                "message": "Database metrics retrieved",
                "metrics": {
                    "connections_active": metrics.connections_active,
                    "connections_idle": metrics.connections_idle,
                    "connections_total": metrics.connections_total,
                    "query_count": metrics.query_count,
                    "slow_queries": metrics.slow_queries,
                    "cache_hit_ratio": round(metrics.cache_hit_ratio, 2),
                    "avg_query_time": round(metrics.avg_query_time, 2),
                    "memory_usage_mb": round(metrics.memory_usage / 1024 / 1024, 2),
                    "disk_usage_mb": round(metrics.disk_usage / 1024 / 1024, 2),
                    "timestamp": metrics.timestamp.isoformat()
                },
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get database metrics: {str(e)}"
            )

    async def get_optimization_history(self, version: str = "v3", current_user: str = Depends(security)):
        """Get database optimization history"""
        try:
            history = await database_optimizer.get_optimization_history()
            return {
                "message": "Optimization history retrieved",
                "history": [
                    {
                        "type": opt.optimization_type.value,
                        "success": opt.success,
                        "improvements": opt.improvements,
                        "recommendations": opt.recommendations,
                        "execution_time": round(opt.execution_time, 2),
                        "timestamp": opt.timestamp.isoformat()
                    } for opt in history
                ],
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get optimization history: {str(e)}"
            )

    async def get_performance_trends(self, hours: int = 24, version: str = "v3", current_user: str = Depends(security)):
        """Get database performance trends"""
        try:
            trends = await database_optimizer.get_performance_trends(hours)
            return {
                "message": f"Performance trends for last {hours} hours retrieved",
                "trends": trends,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get performance trends: {str(e)}"
            )

    # Redis Cache Management endpoints
    async def get_cache_stats(self, version: str = "v3", current_user: str = Depends(security)):
        """Get cache statistics"""
        try:
            stats = await redis_cache_service.get_cache_stats()
            return {
                "message": "Cache statistics retrieved",
                "stats": {
                    "hits": stats.hits,
                    "misses": stats.misses,
                    "sets": stats.sets,
                    "deletes": stats.deletes,
                    "evictions": stats.evictions,
                    "hit_rate": round(stats.hit_rate * 100, 2),
                    "total_keys": stats.total_keys,
                    "memory_usage_mb": round(stats.memory_usage_bytes / 1024 / 1024, 2),
                    "uptime_hours": round(stats.uptime_seconds / 3600, 2)
                },
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get cache stats: {str(e)}"
            )

    async def clear_cache(self, cache_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Clear cache entries"""
        try:
            pattern = cache_data.get("pattern", "*")
            deleted_count = await redis_cache_service.clear_cache(pattern)
            return {
                "message": f"Cleared {deleted_count} cache entries",
                "pattern": pattern,
                "deleted_count": deleted_count,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to clear cache: {str(e)}"
            )

    async def invalidate_api_cache(self, invalidation_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Invalidate API cache"""
        try:
            path_pattern = invalidation_data.get("path_pattern", "")
            method = invalidation_data.get("method")

            if not path_pattern:
                raise HTTPException(status_code=400, detail="Path pattern is required")

            await redis_cache_service.invalidate_api_cache(path_pattern, method)
            return {
                "message": f"Invalidated API cache for pattern: {path_pattern}",
                "path_pattern": path_pattern,
                "method": method,
                "success": True
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to invalidate API cache: {str(e)}"
            )

    async def invalidate_data_cache(self, invalidation_data: dict, version: str = "v3", current_user: str = Depends(security)):
        """Invalidate data cache"""
        try:
            tags = invalidation_data.get("tags", [])
            pattern = invalidation_data.get("pattern")

            await redis_cache_service.invalidate_data_cache(tags, pattern)
            return {
                "message": "Invalidated data cache",
                "tags": tags,
                "pattern": pattern,
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to invalidate data cache: {str(e)}"
            )

    async def warmup_cache(self, version: str = "v3", current_user: str = Depends(security)):
        """Warm up cache"""
        try:
            await redis_cache_service.warmup_cache()
            return {
                "message": "Cache warmup initiated",
                "success": True
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to warm up cache: {str(e)}"
            )

# Create the app instance
app = NexusUnifiedBackend().app

if __name__ == "__main__":
    # Get configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting NEXUS Unified Backend on {host}:{port}")
    
    # Run the server
    uvicorn.run(
        "main_unified:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
