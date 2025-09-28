# 🔒 Frenly AI - Security Guide

## Overview

This guide provides comprehensive security information for the Frenly AI, including best practices, configuration, and incident response.

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────┐
│           Application Layer         │
├─────────────────────────────────────┤
│           API Security              │
├─────────────────────────────────────┤
│           Authentication            │
├─────────────────────────────────────┤
│           Authorization             │
├─────────────────────────────────────┤
│           Data Encryption           │
├─────────────────────────────────────┤
│           Network Security          │
└─────────────────────────────────────┘
```

### Security Principles

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimal required permissions
3. **Zero Trust**: Verify everything, trust nothing
4. **Security by Design**: Built-in security features
5. **Regular Updates**: Keep system updated

## Authentication & Authorization

### API Key Authentication

#### Basic API Key Setup

```json
{
  "security": {
    "api_key_required": true,
    "api_key": "your-secure-api-key-here",
    "api_key_header": "X-API-Key"
  }
}
```

#### Advanced API Key Management

```python
import hashlib
import secrets
from datetime import datetime, timedelta

class APIKeyManager:
    def __init__(self):
        self.api_keys = {}
        self.key_expiry = {}

    def generate_api_key(self, user_id, expires_in_days=30):
        """Generate a secure API key"""
        key = secrets.token_urlsafe(32)
        hashed_key = hashlib.sha256(key.encode()).hexdigest()

        self.api_keys[hashed_key] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'permissions': ['read', 'write']
        }

        self.key_expiry[hashed_key] = datetime.now() + timedelta(days=expires_in_days)

        return key

    def validate_api_key(self, api_key):
        """Validate API key"""
        hashed_key = hashlib.sha256(api_key.encode()).hexdigest()

        if hashed_key not in self.api_keys:
            return False

        if datetime.now() > self.key_expiry.get(hashed_key, datetime.min):
            del self.api_keys[hashed_key]
            del self.key_expiry[hashed_key]
            return False

        return True
```

### JWT Authentication

#### JWT Implementation

```python
import jwt
from datetime import datetime, timedelta
import secrets

class JWTAuth:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.algorithm = 'HS256'
        self.expiry_hours = 24

    def generate_token(self, user_id, permissions=None):
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'permissions': permissions or ['read'],
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=self.expiry_hours)
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def validate_token(self, token):
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
```

### Role-Based Access Control (RBAC)

#### Permission System

```python
from enum import Enum
from typing import Set, List

class Permission(Enum):
    READ_TASKS = "read:tasks"
    WRITE_TASKS = "write:tasks"
    DELETE_TASKS = "delete:tasks"
    READ_AGENT = "read:agent"
    WRITE_AGENT = "write:agent"
    ADMIN = "admin"

class Role:
    def __init__(self, name: str, permissions: Set[Permission]):
        self.name = name
        self.permissions = permissions

    def has_permission(self, permission: Permission) -> bool:
        return permission in self.permissions

class User:
    def __init__(self, user_id: str, roles: List[Role]):
        self.user_id = user_id
        self.roles = roles

    def has_permission(self, permission: Permission) -> bool:
        return any(role.has_permission(permission) for role in self.roles)

# Define roles
ADMIN_ROLE = Role("admin", {Permission.ADMIN})
USER_ROLE = Role("user", {Permission.READ_TASKS, Permission.WRITE_TASKS})
READONLY_ROLE = Role("readonly", {Permission.READ_TASKS})
```

## Data Protection

### Encryption at Rest

#### Database Encryption

```python
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self, key=None):
        if key is None:
            key = Fernet.generate_key()
        self.cipher = Fernet(key)

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        encrypted_bytes = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(encrypted_bytes)
        return decrypted_data.decode()

# Usage
encryption = DataEncryption()

# Encrypt sensitive configuration
encrypted_config = encryption.encrypt_data("sensitive_config_value")

# Decrypt when needed
decrypted_config = encryption.decrypt_data(encrypted_config)
```

#### File Encryption

```python
import os
from cryptography.fernet import Fernet

class FileEncryption:
    def __init__(self, key_file='encryption.key'):
        self.key_file = key_file
        self.key = self._load_or_generate_key()
        self.cipher = Fernet(self.key)

    def _load_or_generate_key(self):
        """Load existing key or generate new one"""
        if os.path.exists(self.key_file):
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            return key

    def encrypt_file(self, input_file, output_file):
        """Encrypt a file"""
        with open(input_file, 'rb') as f:
            data = f.read()

        encrypted_data = self.cipher.encrypt(data)

        with open(output_file, 'wb') as f:
            f.write(encrypted_data)

    def decrypt_file(self, input_file, output_file):
        """Decrypt a file"""
        with open(input_file, 'rb') as f:
            encrypted_data = f.read()

        decrypted_data = self.cipher.decrypt(encrypted_data)

        with open(output_file, 'wb') as f:
            f.write(decrypted_data)
```

### Encryption in Transit

#### HTTPS/TLS Configuration

```python
import ssl
import aiohttp

class SecureHTTPClient:
    def __init__(self, cert_file=None, key_file=None):
        self.cert_file = cert_file
        self.key_file = key_file
        self.ssl_context = self._create_ssl_context()

    def _create_ssl_context(self):
        """Create secure SSL context"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED

        if self.cert_file and self.key_file:
            context.load_cert_chain(self.cert_file, self.key_file)

        return context

    async def make_secure_request(self, url, method='GET', **kwargs):
        """Make secure HTTPS request"""
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.request(method, url, **kwargs) as response:
                return await response.json()
```

#### WebSocket Security

```python
import websockets
import ssl

class SecureWebSocket:
    def __init__(self, cert_file=None, key_file=None):
        self.cert_file = cert_file
        self.key_file = key_file
        self.ssl_context = self._create_ssl_context()

    def _create_ssl_context(self):
        """Create SSL context for WebSocket"""
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.cert_file, self.key_file)
        return context

    async def start_secure_server(self, host, port, handler):
        """Start secure WebSocket server"""
        return await websockets.serve(
            handler,
            host,
            port,
            ssl=self.ssl_context
        )
```

## Input Validation & Sanitization

### Input Validation

```python
import re
from typing import Any, Dict, List
from dataclasses import dataclass

@dataclass
class ValidationRule:
    field: str
    required: bool = False
    min_length: int = None
    max_length: int = None
    pattern: str = None
    data_type: type = str

class InputValidator:
    def __init__(self):
        self.rules = {}

    def add_rule(self, rule: ValidationRule):
        """Add validation rule"""
        self.rules[rule.field] = rule

    def validate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Validate input data"""
        errors = {}

        for field, rule in self.rules.items():
            value = data.get(field)

            # Check required fields
            if rule.required and value is None:
                errors.setdefault(field, []).append(f"{field} is required")
                continue

            if value is None:
                continue

            # Check data type
            if not isinstance(value, rule.data_type):
                errors.setdefault(field, []).append(
                    f"{field} must be of type {rule.data_type.__name__}"
                )
                continue

            # Check string length
            if isinstance(value, str):
                if rule.min_length and len(value) < rule.min_length:
                    errors.setdefault(field, []).append(
                        f"{field} must be at least {rule.min_length} characters"
                    )

                if rule.max_length and len(value) > rule.max_length:
                    errors.setdefault(field, []).append(
                        f"{field} must be at most {rule.max_length} characters"
                    )

                # Check pattern
                if rule.pattern and not re.match(rule.pattern, value):
                    errors.setdefault(field, []).append(
                        f"{field} format is invalid"
                    )

        return errors

# Usage
validator = InputValidator()
validator.add_rule(ValidationRule(
    field="username",
    required=True,
    min_length=3,
    max_length=20,
    pattern=r"^[a-zA-Z0-9_]+$"
))
validator.add_rule(ValidationRule(
    field="email",
    required=True,
    pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
))

# Validate data
data = {"username": "user123", "email": "user@example.com"}
errors = validator.validate(data)
```

### SQL Injection Prevention

```python
import asyncpg
from typing import Any, Dict, List

class SecureDatabase:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None

    async def connect(self):
        """Connect to database with connection pooling"""
        self.pool = await asyncpg.create_pool(
            self.connection_string,
            min_size=5,
            max_size=20
        )

    async def execute_query(self, query: str, params: List[Any] = None):
        """Execute query with parameterized statements"""
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *(params or []))

    async def get_user_by_id(self, user_id: int):
        """Get user by ID (safe from SQL injection)"""
        query = "SELECT * FROM users WHERE id = $1"
        return await self.execute_query(query, [user_id])

    async def search_users(self, search_term: str):
        """Search users (safe from SQL injection)"""
        query = "SELECT * FROM users WHERE username ILIKE $1"
        return await self.execute_query(query, [f"%{search_term}%"])

# Bad example (vulnerable to SQL injection)
def get_user_unsafe(user_id: str):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    # This is vulnerable to SQL injection!

# Good example (safe from SQL injection)
async def get_user_safe(user_id: int):
    query = "SELECT * FROM users WHERE id = $1"
    return await db.execute_query(query, [user_id])
```

### XSS Prevention

```python
import html
import re
from typing import str

class XSSProtection:
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Sanitize HTML to prevent XSS"""
        # Escape HTML characters
        sanitized = html.escape(text)

        # Remove script tags
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Remove javascript: URLs
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)

        # Remove on* event handlers
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL to prevent malicious redirects"""
        # Allow only http and https protocols
        allowed_protocols = ['http:', 'https:']

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.scheme in allowed_protocols
        except:
            return False

# Usage
xss_protection = XSSProtection()

# Sanitize user input
user_input = "<script>alert('XSS')</script>Hello World"
sanitized = xss_protection.sanitize_html(user_input)
# Result: "&lt;script&gt;alert('XSS')&lt;/script&gt;Hello World"

# Validate URL
malicious_url = "javascript:alert('XSS')"
is_valid = xss_protection.validate_url(malicious_url)
# Result: False
```

## Network Security

### Firewall Configuration

#### iptables Rules

```bash
#!/bin/bash
# Firewall configuration for Frenly system

# Clear existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback traffic
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (change port if needed)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow HTTP and HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow Frenly port (change if different)
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# Allow ICMP (ping)
iptables -A INPUT -p icmp -j ACCEPT

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: " --log-level 4

# Save rules
iptables-save > /etc/iptables/rules.v4
```

#### UFW Configuration

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Frenly port
sudo ufw allow 8080/tcp

# Deny all other incoming traffic
sudo ufw default deny incoming

# Allow all outgoing traffic
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

### Rate Limiting

```python
import time
from collections import defaultdict, deque
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)

    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """Check if request is allowed for client IP"""
        now = time.time()
        client_requests = self.requests[client_ip]

        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()

        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True, self.max_requests - len(client_requests)
        else:
            return False, 0

    def get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests for client IP"""
        now = time.time()
        client_requests = self.requests[client_ip]

        # Remove old requests
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()

        return max(0, self.max_requests - len(client_requests))

# Usage in API handler
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

async def api_handler(request):
    client_ip = request.remote
    allowed, remaining = rate_limiter.is_allowed(client_ip)

    if not allowed:
        return web.json_response(
            {"error": "Rate limit exceeded"},
            status=429,
            headers={"Retry-After": "60"}
        )

    # Process request
    return web.json_response({"remaining": remaining})
```

### DDoS Protection

```python
import asyncio
import time
from collections import defaultdict

class DDoSProtection:
    def __init__(self, max_requests_per_second: int = 10, ban_duration: int = 300):
        self.max_requests_per_second = max_requests_per_second
        self.ban_duration = ban_duration
        self.request_counts = defaultdict(list)
        self.banned_ips = {}

    def is_banned(self, client_ip: str) -> bool:
        """Check if IP is banned"""
        if client_ip in self.banned_ips:
            if time.time() - self.banned_ips[client_ip] > self.ban_duration:
                del self.banned_ips[client_ip]
                return False
            return True
        return False

    def check_request(self, client_ip: str) -> bool:
        """Check if request should be allowed"""
        if self.is_banned(client_ip):
            return False

        now = time.time()
        client_requests = self.request_counts[client_ip]

        # Remove requests older than 1 second
        client_requests[:] = [req_time for req_time in client_requests if now - req_time < 1.0]

        # Check rate limit
        if len(client_requests) > self.max_requests_per_second:
            self.banned_ips[client_ip] = now
            return False

        # Add current request
        client_requests.append(now)
        return True

# Usage
ddos_protection = DDoSProtection(max_requests_per_second=10, ban_duration=300)

async def protected_handler(request):
    client_ip = request.remote

    if not ddos_protection.check_request(client_ip):
        return web.json_response(
            {"error": "Request blocked"},
            status=429
        )

    # Process request
    return web.json_response({"status": "ok"})
```

## Security Monitoring

### Audit Logging

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class SecurityAuditLogger:
    def __init__(self, log_file: str = "security_audit.log"):
        self.logger = logging.getLogger("security_audit")
        self.logger.setLevel(logging.INFO)

        # Create file handler
        handler = logging.FileHandler(log_file)
        handler.setLevel(logging.INFO)

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def log_login_attempt(self, user_id: str, ip_address: str, success: bool):
        """Log login attempt"""
        event = {
            "event_type": "login_attempt",
            "user_id": user_id,
            "ip_address": ip_address,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(event))

    def log_api_access(self, endpoint: str, method: str, ip_address: str, user_id: str = None):
        """Log API access"""
        event = {
            "event_type": "api_access",
            "endpoint": endpoint,
            "method": method,
            "ip_address": ip_address,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(json.dumps(event))

    def log_security_violation(self, violation_type: str, details: Dict[str, Any]):
        """Log security violation"""
        event = {
            "event_type": "security_violation",
            "violation_type": violation_type,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.warning(json.dumps(event))

# Usage
audit_logger = SecurityAuditLogger()

# Log events
audit_logger.log_login_attempt("user123", "192.168.1.100", True)
audit_logger.log_api_access("/api/tasks", "GET", "192.168.1.100", "user123")
audit_logger.log_security_violation("rate_limit_exceeded", {
    "ip_address": "192.168.1.100",
    "requests_per_second": 15
})
```

### Intrusion Detection

```python
import re
from typing import List, Dict, Any
from collections import defaultdict

class IntrusionDetectionSystem:
    def __init__(self):
        self.suspicious_patterns = [
            r"union\s+select",
            r"drop\s+table",
            r"delete\s+from",
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"\.\./",
            r"\.\.\\",
            r"eval\s*\(",
            r"exec\s*\("
        ]
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.suspicious_patterns]
        self.suspicious_ips = defaultdict(int)
        self.threshold = 5

    def analyze_request(self, request_data: Dict[str, Any]) -> bool:
        """Analyze request for suspicious activity"""
        is_suspicious = False

        # Check for SQL injection patterns
        for pattern in self.compiled_patterns:
            if pattern.search(str(request_data)):
                is_suspicious = True
                break

        # Check for XSS patterns
        if any(tag in str(request_data).lower() for tag in ['<script>', 'javascript:', 'onclick=']):
            is_suspicious = True

        # Check for path traversal
        if any(path in str(request_data) for path in ['../', '..\\']):
            is_suspicious = True

        return is_suspicious

    def track_suspicious_ip(self, ip_address: str):
        """Track suspicious IP addresses"""
        self.suspicious_ips[ip_address] += 1

        if self.suspicious_ips[ip_address] >= self.threshold:
            self._block_ip(ip_address)

    def _block_ip(self, ip_address: str):
        """Block suspicious IP address"""
        # Implement IP blocking logic
        print(f"Blocking suspicious IP: {ip_address}")

# Usage
ids = IntrusionDetectionSystem()

# Analyze request
request_data = {"query": "SELECT * FROM users WHERE id = 1 UNION SELECT * FROM passwords"}
is_suspicious = ids.analyze_request(request_data)

if is_suspicious:
    ids.track_suspicious_ip("192.168.1.100")
```

## Incident Response

### Security Incident Response Plan

#### 1. Detection

```python
class SecurityIncidentDetector:
    def __init__(self):
        self.incident_types = {
            "brute_force": self._detect_brute_force,
            "sql_injection": self._detect_sql_injection,
            "xss_attempt": self._detect_xss,
            "rate_limit_exceeded": self._detect_rate_limit
        }

    def detect_incident(self, request_data: Dict[str, Any]) -> List[str]:
        """Detect security incidents"""
        incidents = []

        for incident_type, detector in self.incident_types.items():
            if detector(request_data):
                incidents.append(incident_type)

        return incidents

    def _detect_brute_force(self, request_data: Dict[str, Any]) -> bool:
        """Detect brute force attacks"""
        # Implement brute force detection logic
        return False

    def _detect_sql_injection(self, request_data: Dict[str, Any]) -> bool:
        """Detect SQL injection attempts"""
        sql_patterns = [r"union\s+select", r"drop\s+table", r"delete\s+from"]
        return any(re.search(pattern, str(request_data), re.IGNORECASE) for pattern in sql_patterns)

    def _detect_xss(self, request_data: Dict[str, Any]) -> bool:
        """Detect XSS attempts"""
        xss_patterns = [r"<script[^>]*>", r"javascript:", r"on\w+\s*="]
        return any(re.search(pattern, str(request_data), re.IGNORECASE) for pattern in xss_patterns)

    def _detect_rate_limit(self, request_data: Dict[str, Any]) -> bool:
        """Detect rate limit violations"""
        # Implement rate limit detection logic
        return False
```

#### 2. Response

```python
class SecurityIncidentResponse:
    def __init__(self):
        self.response_actions = {
            "brute_force": self._handle_brute_force,
            "sql_injection": self._handle_sql_injection,
            "xss_attempt": self._handle_xss,
            "rate_limit_exceeded": self._handle_rate_limit
        }

    def respond_to_incident(self, incident_type: str, request_data: Dict[str, Any]):
        """Respond to security incident"""
        if incident_type in self.response_actions:
            self.response_actions[incident_type](request_data)

    def _handle_brute_force(self, request_data: Dict[str, Any]):
        """Handle brute force attack"""
        # Block IP address
        # Log incident
        # Send alert
        pass

    def _handle_sql_injection(self, request_data: Dict[str, Any]):
        """Handle SQL injection attempt"""
        # Block request
        # Log incident
        # Send alert
        pass

    def _handle_xss(self, request_data: Dict[str, Any]):
        """Handle XSS attempt"""
        # Block request
        # Log incident
        # Send alert
        pass

    def _handle_rate_limit(self, request_data: Dict[str, Any]):
        """Handle rate limit violation"""
        # Block IP temporarily
        # Log incident
        pass
```

### Security Checklist

#### Pre-deployment Security Checklist

- [ ] **Authentication**: Implement strong authentication
- [ ] **Authorization**: Set up proper access controls
- [ ] **Encryption**: Enable encryption for data at rest and in transit
- [ ] **Input Validation**: Validate all user inputs
- [ ] **Output Encoding**: Encode all outputs
- [ ] **Error Handling**: Implement secure error handling
- [ ] **Logging**: Set up comprehensive logging
- [ ] **Monitoring**: Implement security monitoring
- [ ] **Updates**: Keep all dependencies updated
- [ ] **Configuration**: Secure configuration management

#### Runtime Security Checklist

- [ ] **Access Logs**: Monitor access logs regularly
- [ ] **Error Logs**: Review error logs for security issues
- [ ] **Performance**: Monitor for unusual performance patterns
- [ ] **Network**: Monitor network traffic
- [ ] **Updates**: Apply security updates promptly
- [ ] **Backups**: Verify backup integrity
- [ ] **Access**: Review user access regularly
- [ ] **Incidents**: Document and respond to incidents

## Security Best Practices

### Development Security

#### Secure Coding Practices

```python
# Good: Use parameterized queries
async def get_user_safe(user_id: int):
    query = "SELECT * FROM users WHERE id = $1"
    return await db.execute_query(query, [user_id])

# Bad: String concatenation (vulnerable to SQL injection)
async def get_user_unsafe(user_id: str):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return await db.execute_query(query)

# Good: Input validation
def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None

# Bad: No input validation
def process_email(email: str):
    # Process without validation
    pass
```

#### Dependency Management

```bash
# Check for vulnerable dependencies
pip install safety
safety check

# Update dependencies regularly
pip install --upgrade -r requirements.txt

# Use dependency scanning
pip install bandit
bandit -r .
```

### Operational Security

#### Regular Security Updates

```bash
#!/bin/bash
# Security update script

# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip install --upgrade -r requirements.txt

# Check for security vulnerabilities
safety check

# Scan for security issues
bandit -r .

# Restart services
sudo systemctl restart nexus
```

#### Security Monitoring

```python
# Security monitoring script
import time
import subprocess
import logging

def monitor_security():
    """Monitor system security"""
    while True:
        # Check for failed login attempts
        check_failed_logins()

        # Check for suspicious processes
        check_suspicious_processes()

        # Check for unusual network activity
        check_network_activity()

        # Check for file integrity
        check_file_integrity()

        time.sleep(300)  # Check every 5 minutes

def check_failed_logins():
    """Check for failed login attempts"""
    result = subprocess.run(
        ["grep", "Failed password", "/var/log/auth.log"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        failed_attempts = len(result.stdout.split('\n'))
        if failed_attempts > 10:
            send_alert(f"High number of failed login attempts: {failed_attempts}")

def check_suspicious_processes():
    """Check for suspicious processes"""
    result = subprocess.run(
        ["ps", "aux"],
        capture_output=True,
        text=True
    )

    suspicious_keywords = ["nc", "netcat", "nmap", "sqlmap"]
    for line in result.stdout.split('\n'):
        for keyword in suspicious_keywords:
            if keyword in line.lower():
                send_alert(f"Suspicious process detected: {line}")

def send_alert(message):
    """Send security alert"""
    logging.warning(f"SECURITY ALERT: {message}")
    # Implement alerting mechanism (email, Slack, etc.)
```

---

**Security Guide v4.0.0**  
_Last updated: September 20, 2025_
