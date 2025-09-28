#!/usr/bin/env python3
"""
NEXUS Platform - Enterprise Integration Hub
Comprehensive integration with third-party systems and external APIs
"""

import asyncio
import json
import logging
import uuid
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import aiohttp
import asyncpg
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.config.settings import get_settings
from .data_transformation_engine import data_transformation_engine

logger = logging.getLogger(__name__)


class IntegrationType(Enum):
    """Integration type enumeration"""

    REST_API = "rest_api"
    GRAPHQL = "graphql"
    SOAP = "soap"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    FILE_SYSTEM = "file_system"
    CLOUD_STORAGE = "cloud_storage"
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    CUSTOM = "custom"


class AuthenticationType(Enum):
    """Authentication type enumeration"""

    NONE = "none"
    BASIC = "basic"
    BEARER_TOKEN = "bearer_token"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    CERTIFICATE = "certificate"


class ConnectionStatus(Enum):
    """Connection status enumeration"""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class IntegrationConnector:
    """Data class for integration connector"""

    connector_id: str
    name: str
    description: str
    integration_type: IntegrationType
    base_url: Optional[str]
    config: Dict[str, Any]
    authentication: Dict[str, Any]
    rate_limits: Dict[str, Any] = field(default_factory=dict)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    transformation_rules: List[Dict[str, Any]] = field(default_factory=list)
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    last_connected: Optional[datetime] = None
    error_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class IntegrationRequest:
    """Data class for integration request"""

    request_id: str
    connector_id: str
    method: str
    endpoint: str
    headers: Dict[str, str]
    params: Dict[str, Any]
    data: Any
    timeout: int
    retry_count: int
    status: str
    response: Any = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None


class EnterpriseIntegrationHub:
    """Enterprise integration hub for third-party systems"""

    def __init__(self):
        self.settings = get_settings()
        self.db_engine = None
        self.redis_client = None

        # HTTP session for API calls
        self.http_session = None

        # Connector registry
        self.connectors: Dict[str, IntegrationConnector] = {}

        # Active connections
        self.active_connections: Dict[str, Any] = {}

        # Rate limiters
        self.rate_limiters: Dict[str, Dict[str, Any]] = {}

        # Built-in connectors
        self._register_builtin_connectors()

    def _register_builtin_connectors(self):
        """Register built-in connector templates"""
        self.builtin_connectors = {
            "slack": {
                "name": "Slack",
                "type": IntegrationType.REST_API,
                "base_url": "https://slack.com/api",
                "auth_type": AuthenticationType.BEARER_TOKEN,
                "endpoints": {
                    "send_message": "/chat.postMessage",
                    "get_channels": "/conversations.list",
                },
            },
            "stripe": {
                "name": "Stripe",
                "type": IntegrationType.REST_API,
                "base_url": "https://api.stripe.com/v1",
                "auth_type": AuthenticationType.BEARER_TOKEN,
                "endpoints": {
                    "create_payment": "/payment_intents",
                    "list_payments": "/payment_intents",
                },
            },
            "salesforce": {
                "name": "Salesforce",
                "type": IntegrationType.REST_API,
                "base_url": "https://login.salesforce.com/services/oauth2/token",
                "auth_type": AuthenticationType.OAUTH2,
                "endpoints": {"query": "/services/data/v57.0/query"},
            },
            "aws_s3": {
                "name": "AWS S3",
                "type": IntegrationType.CLOUD_STORAGE,
                "auth_type": AuthenticationType.API_KEY,
                "endpoints": {
                    "upload": "s3.amazonaws.com/{bucket}/{key}",
                    "download": "s3.amazonaws.com/{bucket}/{key}",
                },
            },
            "sendgrid": {
                "name": "SendGrid",
                "type": IntegrationType.EMAIL,
                "base_url": "https://api.sendgrid.com/v3",
                "auth_type": AuthenticationType.BEARER_TOKEN,
                "endpoints": {"send_email": "/mail/send"},
            },
            "twilio": {
                "name": "Twilio",
                "type": IntegrationType.SMS,
                "base_url": "https://api.twilio.com/2010-04-01",
                "auth_type": AuthenticationType.BASIC,
                "endpoints": {"send_sms": "/Accounts/{account_sid}/Messages.json"},
            },
        }

    async def initialize(self):
        """Initialize the integration hub"""
        try:
            # Database connection
            self.db_engine = create_async_engine(
                self.settings.database_url, echo=False, pool_size=10, max_overflow=20
            )

            # Redis connection
            self.redis_client = redis.Redis(
                host=self.settings.redis_host,
                port=self.settings.redis_port,
                db=self.settings.redis_db,
                decode_responses=True,
            )

            # HTTP session
            self.http_session = aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=100, ttl_dns_cache=300),
                timeout=aiohttp.ClientTimeout(total=30),
            )

            # Create tables
            await self._create_tables()

            # Load connectors
            await self._load_connectors()

            logger.info("Enterprise integration hub initialized")

        except Exception as e:
            logger.error(f"Failed to initialize integration hub: {e}")
            raise

    async def _create_tables(self):
        """Create necessary database tables"""
        try:
            async with self.db_engine.begin() as conn:
                # Integration connectors table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS integration_connectors (
                        connector_id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        integration_type VARCHAR(50) NOT NULL,
                        base_url TEXT,
                        config JSONB,
                        authentication JSONB,
                        rate_limits JSONB,
                        retry_policy JSONB,
                        transformation_rules JSONB,
                        status VARCHAR(50) DEFAULT 'disconnected',
                        last_connected TIMESTAMP WITH TIME ZONE,
                        error_count INTEGER DEFAULT 0,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                    )
                )

                # Integration requests table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS integration_requests (
                        request_id VARCHAR(255) PRIMARY KEY,
                        connector_id VARCHAR(255) NOT NULL,
                        method VARCHAR(10) NOT NULL,
                        endpoint TEXT NOT NULL,
                        headers JSONB,
                        params JSONB,
                        data JSONB,
                        timeout INTEGER,
                        retry_count INTEGER DEFAULT 0,
                        status VARCHAR(50) NOT NULL,
                        response JSONB,
                        error_message TEXT,
                        started_at TIMESTAMP WITH TIME ZONE,
                        completed_at TIMESTAMP WITH TIME ZONE,
                        execution_time FLOAT
                    )
                """
                    )
                )

                # Integration logs table
                await conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS integration_logs (
                        log_id SERIAL PRIMARY KEY,
                        connector_id VARCHAR(255),
                        request_id VARCHAR(255),
                        level VARCHAR(20),
                        message TEXT,
                        metadata JSONB,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """
                    )
                )

        except Exception as e:
            logger.error(f"Failed to create integration tables: {e}")
            raise

    async def _load_connectors(self):
        """Load connectors from database"""
        try:
            async with self.db_engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT connector_id, name, description, integration_type, base_url,
                           config, authentication, rate_limits, retry_policy, transformation_rules,
                           status, last_connected, error_count, created_at, updated_at
                    FROM integration_connectors
                """
                    )
                )

                rows = result.fetchall()
                for row in rows:
                    connector = IntegrationConnector(
                        connector_id=row[0],
                        name=row[1],
                        description=row[2],
                        integration_type=IntegrationType(row[3]),
                        base_url=row[4],
                        config=row[5] or {},
                        authentication=row[6] or {},
                        rate_limits=row[7] or {},
                        retry_policy=row[8] or {},
                        transformation_rules=row[9] or [],
                        status=ConnectionStatus(row[10] or "disconnected"),
                        last_connected=row[11],
                        error_count=row[12] or 0,
                        created_at=row[13],
                        updated_at=row[14],
                    )
                    self.connectors[connector.connector_id] = connector

        except Exception as e:
            logger.error(f"Failed to load connectors: {e}")

    async def create_connector(
        self,
        name: str,
        description: str,
        integration_type: IntegrationType,
        base_url: Optional[str] = None,
        config: Dict[str, Any] = None,
        authentication: Dict[str, Any] = None,
    ) -> Optional[str]:
        """Create a new integration connector"""
        try:
            connector_id = f"conn_{uuid.uuid4().hex}"

            connector = IntegrationConnector(
                connector_id=connector_id,
                name=name,
                description=description,
                integration_type=integration_type,
                base_url=base_url,
                config=config or {},
                authentication=authentication or {},
                rate_limits={"requests_per_minute": 60, "burst_limit": 10},
                retry_policy={"max_retries": 3, "backoff_factor": 2.0},
            )

            # Store connector
            await self._store_connector(connector)

            # Add to registry
            self.connectors[connector_id] = connector

            logger.info(f"Integration connector {connector_id} created")
            return connector_id

        except Exception as e:
            logger.error(f"Failed to create connector: {e}")
            return None

    async def create_connector_from_template(
        self, template_name: str, name: str, description: str, config: Dict[str, Any]
    ) -> Optional[str]:
        """Create a connector from a built-in template"""
        try:
            if template_name not in self.builtin_connectors:
                logger.error(f"Template {template_name} not found")
                return None

            template = self.builtin_connectors[template_name]

            connector_id = await self.create_connector(
                name=name,
                description=description,
                integration_type=template["type"],
                base_url=template.get("base_url"),
                config={**template, **config},
            )

            return connector_id

        except Exception as e:
            logger.error(
                f"Failed to create connector from template {template_name}: {e}"
            )
            return None

    async def update_connector_auth(
        self,
        connector_id: str,
        auth_type: AuthenticationType,
        auth_config: Dict[str, Any],
    ) -> bool:
        """Update connector authentication"""
        try:
            if connector_id not in self.connectors:
                logger.error(f"Connector {connector_id} not found")
                return False

            connector = self.connectors[connector_id]
            connector.authentication = {"type": auth_type.value, **auth_config}
            connector.updated_at = datetime.now(timezone.utc)

            # Store updated connector
            await self._store_connector(connector)

            logger.info(f"Authentication updated for connector {connector_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to update connector auth: {e}")
            return False

    async def test_connection(self, connector_id: str) -> Tuple[bool, str]:
        """Test connection to external system"""
        try:
            if connector_id not in self.connectors:
                return False, "Connector not found"

            connector = self.connectors[connector_id]

            # Test based on integration type
            if connector.integration_type == IntegrationType.REST_API:
                success, message = await self._test_rest_api_connection(connector)
            elif connector.integration_type == IntegrationType.DATABASE:
                success, message = await self._test_database_connection(connector)
            else:
                return True, "Connection test not implemented for this integration type"

            # Update connector status
            if success:
                connector.status = ConnectionStatus.CONNECTED
                connector.last_connected = datetime.now(timezone.utc)
                connector.error_count = 0
            else:
                connector.status = ConnectionStatus.ERROR
                connector.error_count += 1

            await self._store_connector(connector)

            return success, message

        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False, str(e)

    async def make_request(
        self,
        connector_id: str,
        method: str,
        endpoint: str,
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        data: Any = None,
        timeout: int = 30,
    ) -> Optional[IntegrationRequest]:
        """Make a request to an external system"""
        try:
            if connector_id not in self.connectors:
                logger.error(f"Connector {connector_id} not found")
                return None

            connector = self.connectors[connector_id]

            # Check rate limits
            if not await self._check_rate_limit(connector_id):
                logger.warning(f"Rate limit exceeded for connector {connector_id}")
                return None

            # Create request
            request_id = f"req_{uuid.uuid4().hex}"
            request = IntegrationRequest(
                request_id=request_id,
                connector_id=connector_id,
                method=method.upper(),
                endpoint=endpoint,
                headers=headers or {},
                params=params or {},
                data=data,
                timeout=timeout,
                retry_count=0,
                status="pending",
            )

            # Execute request
            await self._execute_request(request, connector)

            return request

        except Exception as e:
            logger.error(f"Failed to make request: {e}")
            return None

    async def _execute_request(
        self, request: IntegrationRequest, connector: IntegrationConnector
    ):
        """Execute an integration request"""
        try:
            request.status = "running"
            request.started_at = datetime.now(timezone.utc)
            await self._store_request(request)

            # Apply authentication
            auth_headers = await self._apply_authentication(connector)

            # Merge headers
            final_headers = {**auth_headers, **request.headers}

            # Execute based on integration type
            if connector.integration_type == IntegrationType.REST_API:
                response = await self._execute_rest_api_request(
                    connector, request, final_headers
                )
            elif connector.integration_type == IntegrationType.SOAP:
                response = await self._execute_soap_request(
                    connector, request, final_headers
                )
            elif connector.integration_type == IntegrationType.DATABASE:
                response = await self._execute_database_request(connector, request)
            else:
                raise ValueError(
                    f"Unsupported integration type: {connector.integration_type}"
                )

            # Apply transformations
            transformed_response = await self._apply_transformations(
                connector, response
            )

            # Update request
            request.status = "completed"
            request.response = transformed_response
            request.completed_at = datetime.now(timezone.utc)
            request.execution_time = (
                request.completed_at - request.started_at
            ).total_seconds()

            await self._store_request(request)
            await self._log_request(request, "INFO", "Request completed successfully")

        except Exception as e:
            logger.error(f"Request execution failed: {e}")

            # Update request with error
            request.status = "failed"
            request.error_message = str(e)
            request.completed_at = datetime.now(timezone.utc)
            if request.started_at:
                request.execution_time = (
                    request.completed_at - request.started_at
                ).total_seconds()

            await self._store_request(request)
            await self._log_request(request, "ERROR", str(e))

    async def _execute_rest_api_request(
        self,
        connector: IntegrationConnector,
        request: IntegrationRequest,
        headers: Dict[str, str],
    ) -> Any:
        """Execute REST API request"""
        try:
            url = f"{connector.base_url.rstrip('/')}/{request.endpoint.lstrip('/')}"

            # Prepare request data
            request_data = None
            if request.data:
                if isinstance(request.data, dict):
                    request_data = json.dumps(request.data)
                    headers["Content-Type"] = "application/json"
                else:
                    request_data = request.data

            async with self.http_session.request(
                request.method,
                url,
                headers=headers,
                params=request.params,
                data=request_data,
                timeout=aiohttp.ClientTimeout(total=request.timeout),
            ) as response:
                # Handle response
                if response.content_type == "application/json":
                    return await response.json()
                else:
                    return await response.text()

        except Exception as e:
            logger.error(f"REST API request failed: {e}")
            raise

    async def _execute_soap_request(
        self,
        connector: IntegrationConnector,
        request: IntegrationRequest,
        headers: Dict[str, str],
    ) -> Any:
        """Execute SOAP request"""
        try:
            # SOAP implementation (simplified)
            url = f"{connector.base_url.rstrip('/')}/{request.endpoint.lstrip('/')}"

            # Add SOAP headers
            soap_headers = {
                "Content-Type": "text/xml; charset=utf-8",
                "SOAPAction": request.headers.get("SOAPAction", ""),
            }
            headers.update(soap_headers)

            async with self.http_session.post(
                url,
                headers=headers,
                data=request.data,
                timeout=aiohttp.ClientTimeout(total=request.timeout),
            ) as response:
                # Parse SOAP response
                response_text = await response.text()
                # In production, use proper SOAP parsing
                return {"soap_response": response_text, "status": response.status}

        except Exception as e:
            logger.error(f"SOAP request failed: {e}")
            raise

    async def _execute_database_request(
        self, connector: IntegrationConnector, request: IntegrationRequest
    ) -> Any:
        """Execute database request"""
        try:
            # Database connection (simplified - in production use connection pooling)
            db_config = connector.config

            if db_config.get("type") == "postgresql":
                conn_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
                conn = await asyncpg.connect(conn_string)

                try:
                    if request.method == "SELECT":
                        result = await conn.fetch(request.endpoint)
                        return [dict(row) for row in result]
                    else:
                        await conn.execute(request.endpoint)
                        return {"success": True}
                finally:
                    await conn.close()

            else:
                raise ValueError(f"Unsupported database type: {db_config.get('type')}")

        except Exception as e:
            logger.error(f"Database request failed: {e}")
            raise

    async def _apply_authentication(
        self, connector: IntegrationConnector
    ) -> Dict[str, str]:
        """Apply authentication to request headers"""
        try:
            auth_config = connector.authentication
            auth_type = auth_config.get("type")

            headers = {}

            if auth_type == AuthenticationType.BASIC.value:
                import base64

                username = auth_config.get("username", "")
                password = auth_config.get("password", "")
                credentials = base64.b64encode(
                    f"{username}:{password}".encode()
                ).decode()
                headers["Authorization"] = f"Basic {credentials}"

            elif auth_type == AuthenticationType.BEARER_TOKEN.value:
                token = auth_config.get("token", "")
                headers["Authorization"] = f"Bearer {token}"

            elif auth_type == AuthenticationType.API_KEY.value:
                key_name = auth_config.get("key_name", "X-API-Key")
                key_value = auth_config.get("key_value", "")
                headers[key_name] = key_value

            elif auth_type == AuthenticationType.OAUTH2.value:
                # OAuth2 implementation (simplified)
                token = await self._get_oauth2_token(connector)
                headers["Authorization"] = f"Bearer {token}"

            return headers

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {}

    async def _get_oauth2_token(self, connector: IntegrationConnector) -> Optional[str]:
        """Get OAuth2 token (simplified implementation)"""
        # In production, implement proper OAuth2 flow with token refresh
        auth_config = connector.authentication

        token_url = auth_config.get("token_url")
        client_id = auth_config.get("client_id")
        client_secret = auth_config.get("client_secret")

        if not all([token_url, client_id, client_secret]):
            return None

        # This is a simplified implementation
        # In production, use proper OAuth2 library
        return "mock_oauth2_token"

    async def _apply_transformations(
        self, connector: IntegrationConnector, response: Any
    ) -> Any:
        """Apply data transformations to response"""
        try:
            for rule in connector.transformation_rules:
                rule_type = rule.get("type")

                if rule_type == "field_mapping":
                    if isinstance(response, dict):
                        response = self._apply_field_mapping(response, rule)
                elif rule_type == "filter":
                    if isinstance(response, list):
                        response = self._apply_filter(response, rule)
                elif rule_type == "rename":
                    if isinstance(response, dict):
                        response = self._apply_rename(response, rule)

            return response

        except Exception as e:
            logger.warning(f"Transformation failed: {e}")
            return response

    def _apply_field_mapping(
        self, data: Dict[str, Any], rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply field mapping transformation"""
        mapping = rule.get("mapping", {})
        result = {}

        for new_field, old_field in mapping.items():
            if old_field in data:
                result[new_field] = data[old_field]

        return result

    def _apply_filter(
        self, data: List[Dict[str, Any]], rule: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply filter transformation"""
        filter_field = rule.get("field")
        filter_value = rule.get("value")

        if filter_field:
            return [item for item in data if item.get(filter_field) == filter_value]

        return data

    def _apply_rename(
        self, data: Dict[str, Any], rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply rename transformation"""
        rename_map = rule.get("rename", {})

        for old_name, new_name in rename_map.items():
            if old_name in data:
                data[new_name] = data.pop(old_name)

        return data

    async def _check_rate_limit(self, connector_id: str) -> bool:
        """Check if request is within rate limits"""
        try:
            connector = self.connectors[connector_id]
            rate_limits = connector.rate_limits

            requests_per_minute = rate_limits.get("requests_per_minute", 60)
            burst_limit = rate_limits.get("burst_limit", 10)

            # Use Redis for rate limiting
            current_minute = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
            key = f"rate_limit:{connector_id}:{current_minute}"

            current_count = await self.redis_client.get(key)
            current_count = int(current_count) if current_count else 0

            if current_count >= requests_per_minute:
                return False

            # Increment counter
            await self.redis_client.incr(key)
            await self.redis_client.expire(key, 60)  # Expire in 1 minute

            return True

        except Exception as e:
            logger.warning(f"Rate limit check failed: {e}")
            return True  # Allow request on error

    async def _test_rest_api_connection(
        self, connector: IntegrationConnector
    ) -> Tuple[bool, str]:
        """Test REST API connection"""
        try:
            if not connector.base_url:
                return False, "No base URL configured"

            # Try a simple GET request
            async with self.http_session.get(
                connector.base_url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return True, f"Connection successful (status: {response.status})"

        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    async def _test_database_connection(
        self, connector: IntegrationConnector
    ) -> Tuple[bool, str]:
        """Test database connection"""
        try:
            db_config = connector.config

            if db_config.get("type") == "postgresql":
                conn_string = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
                conn = await asyncpg.connect(conn_string)
                await conn.close()
                return True, "Database connection successful"
            else:
                return False, f"Unsupported database type: {db_config.get('type')}"

        except Exception as e:
            return False, f"Database connection failed: {str(e)}"

    async def get_connector_status(self, connector_id: str) -> Optional[Dict[str, Any]]:
        """Get connector status and metrics"""
        try:
            if connector_id not in self.connectors:
                return None

            connector = self.connectors[connector_id]

            # Get recent request stats
            async with self.db_engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT
                        COUNT(*) as total_requests,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_requests,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_requests,
                        AVG(execution_time) as avg_execution_time,
                        MAX(completed_at) as last_request
                    FROM integration_requests
                    WHERE connector_id = $1 AND completed_at >= NOW() - INTERVAL '24 hours'
                """
                    ),
                    (connector_id,),
                )

                row = result.fetchone()

            status_info = {
                "connector_id": connector_id,
                "name": connector.name,
                "status": connector.status.value,
                "integration_type": connector.integration_type.value,
                "last_connected": connector.last_connected.isoformat()
                if connector.last_connected
                else None,
                "error_count": connector.error_count,
                "stats_24h": {
                    "total_requests": row[0] or 0,
                    "successful_requests": row[1] or 0,
                    "failed_requests": row[2] or 0,
                    "avg_execution_time": float(row[3]) if row[3] else 0,
                    "last_request": row[4].isoformat() if row[4] else None,
                },
            }

            return status_info

        except Exception as e:
            logger.error(f"Failed to get connector status: {e}")
            return None

    async def _apply_transformations(
        self, connector: IntegrationConnector, data: Any
    ) -> Any:
        """Apply data transformations to response"""
        try:
            if not connector.transformation_rules:
                return data

            transformed_data = data
            for rule_config in connector.transformation_rules:
                rule_id = rule_config.get("rule_id")
                if rule_id:
                    # Apply transformation using the data transformation engine
                    result = await data_transformation_engine.apply_transformation(
                        rule_id=rule_id,
                        data=transformed_data,
                        additional_context={"connector": connector.connector_id},
                    )

                    if result.success:
                        transformed_data = result.transformed_data
                    else:
                        logger.warning(
                            f"Transformation {rule_id} failed: {result.errors}"
                        )

            return transformed_data

        except Exception as e:
            logger.error(f"Failed to apply transformations: {e}")
            return data

    async def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        try:
            stats = {
                "connectors": {
                    "total": len(self.connectors),
                    "connected": len(
                        [
                            c
                            for c in self.connectors.values()
                            if c.status == ConnectionStatus.CONNECTED
                        ]
                    ),
                    "disconnected": len(
                        [
                            c
                            for c in self.connectors.values()
                            if c.status == ConnectionStatus.DISCONNECTED
                        ]
                    ),
                    "error": len(
                        [
                            c
                            for c in self.connectors.values()
                            if c.status == ConnectionStatus.ERROR
                        ]
                    ),
                },
                "requests_24h": {},
            }

            # Get request statistics from database
            async with self.db_engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT
                        COUNT(*) as total_requests,
                        COUNT(*) FILTER (WHERE status = 'completed') as successful_requests,
                        COUNT(*) FILTER (WHERE status = 'failed') as failed_requests,
                        AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_execution_time,
                        MAX(completed_at) as last_request
                    FROM integration_requests
                    WHERE started_at >= NOW() - INTERVAL '24 hours'
                """
                    )
                )

                row = result.fetchone()
                if row:
                    stats["requests_24h"] = {
                        "total": row[0] or 0,
                        "successful": row[1] or 0,
                        "failed": row[2] or 0,
                        "avg_execution_time": float(row[3]) if row[3] else 0,
                        "last_request": row[4].isoformat() if row[4] else None,
                    }

            return stats

        except Exception as e:
            logger.error(f"Failed to get integration stats: {e}")
            return {
                "connectors": {
                    "total": 0,
                    "connected": 0,
                    "disconnected": 0,
                    "error": 0,
                },
                "requests_24h": {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                    "avg_execution_time": 0,
                    "last_request": None,
                },
            }

    async def _store_connector(self, connector: IntegrationConnector):
        """Store connector in database"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    INSERT INTO integration_connectors
                    (connector_id, name, description, integration_type, base_url, config,
                     authentication, rate_limits, retry_policy, transformation_rules,
                     status, last_connected, error_count, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                    ON CONFLICT (connector_id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        integration_type = EXCLUDED.integration_type,
                        base_url = EXCLUDED.base_url,
                        config = EXCLUDED.config,
                        authentication = EXCLUDED.authentication,
                        rate_limits = EXCLUDED.rate_limits,
                        retry_policy = EXCLUDED.retry_policy,
                        transformation_rules = EXCLUDED.transformation_rules,
                        status = EXCLUDED.status,
                        last_connected = EXCLUDED.last_connected,
                        error_count = EXCLUDED.error_count,
                        updated_at = EXCLUDED.updated_at
                """
                    ),
                    (
                        connector.connector_id,
                        connector.name,
                        connector.description,
                        connector.integration_type.value,
                        connector.base_url,
                        json.dumps(connector.config),
                        json.dumps(connector.authentication),
                        json.dumps(connector.rate_limits),
                        json.dumps(connector.retry_policy),
                        json.dumps(connector.transformation_rules),
                        connector.status.value,
                        connector.last_connected,
                        connector.error_count,
                        connector.updated_at,
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to store connector: {e}")

    async def _store_request(self, request: IntegrationRequest):
        """Store request in database"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    INSERT INTO integration_requests
                    (request_id, connector_id, method, endpoint, headers, params, data,
                     timeout, retry_count, status, response, error_message, started_at,
                     completed_at, execution_time)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                    ON CONFLICT (request_id) DO UPDATE SET
                        retry_count = EXCLUDED.retry_count,
                        status = EXCLUDED.status,
                        response = EXCLUDED.response,
                        error_message = EXCLUDED.error_message,
                        completed_at = EXCLUDED.completed_at,
                        execution_time = EXCLUDED.execution_time
                """
                    ),
                    (
                        request.request_id,
                        request.connector_id,
                        request.method,
                        request.endpoint,
                        json.dumps(request.headers),
                        json.dumps(request.params),
                        json.dumps(request.data)
                        if isinstance(request.data, dict)
                        else request.data,
                        request.timeout,
                        request.retry_count,
                        request.status,
                        json.dumps(request.response)
                        if isinstance(request.response, dict)
                        else request.response,
                        request.error_message,
                        request.started_at,
                        request.completed_at,
                        request.execution_time,
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to store request: {e}")

    async def _log_request(
        self,
        request: IntegrationRequest,
        level: str,
        message: str,
        metadata: Dict[str, Any] = None,
    ):
        """Log integration request"""
        try:
            async with self.db_engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                    INSERT INTO integration_logs
                    (connector_id, request_id, level, message, metadata)
                    VALUES ($1, $2, $3, $4, $5)
                """
                    ),
                    (
                        request.connector_id,
                        request.request_id,
                        level,
                        message,
                        json.dumps(metadata or {}),
                    ),
                )

        except Exception as e:
            logger.error(f"Failed to log request: {e}")


# Global enterprise integration hub instance
enterprise_integration_hub = EnterpriseIntegrationHub()
