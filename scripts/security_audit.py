#!/usr/bin/env python3
"""
NEXUS Platform - Security Audit System
Comprehensive security assessment and penetration testing
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import redis
import requests
import sqlalchemy
import yaml
from docker.errors import DockerException
from sqlalchemy import create_engine, text

import docker

logger = logging.getLogger(__name__)


class SecurityAudit:
    """Comprehensive security audit for NEXUS Platform"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "overall_score": 0,
            "critical_issues": [],
            "high_issues": [],
            "medium_issues": [],
            "low_issues": [],
            "recommendations": [],
        }

    def run_full_audit(self) -> Dict[str, Any]:
        """Run comprehensive security audit"""
        logger.info("Starting comprehensive security audit...")

        # Run all audit checks
        self._audit_authentication()
        self._audit_authorization()
        self._audit_input_validation()
        self._audit_sql_injection()
        self._audit_xss_protection()
        self._audit_csrf_protection()
        self._audit_ssl_tls()
        self._audit_security_headers()
        self._audit_rate_limiting()
        self._audit_file_uploads()
        self._audit_api_security()
        self._audit_database_security()
        self._audit_docker_security()
        self._audit_infrastructure_security()

        # Calculate overall score
        self._calculate_security_score()

        # Generate recommendations
        self._generate_recommendations()

        logger.info("Security audit completed")
        return self.results

    def _audit_authentication(self):
        """Audit authentication mechanisms"""
        logger.info("Auditing authentication...")

        try:
            # Test weak passwords
            weak_passwords = ["password", "123456", "admin", "nexus", "test"]
            for password in weak_passwords:
                response = requests.post(
                    "http://localhost:8001/api/v1/auth/token",
                    data={"username": "admin", "password": password},
                    timeout=5,
                )
                if response.status_code == 200:
                    self.results["critical_issues"].append(
                        {
                            "category": "Authentication",
                            "issue": "Weak password detected",
                            "description": f'Password "{password}" is accepted',
                            "severity": "Critical",
                        }
                    )

            # Test password complexity
            if not self._check_password_policy():
                self.results["high_issues"].append(
                    {
                        "category": "Authentication",
                        "issue": "Weak password policy",
                        "description": "Password policy does not enforce complexity requirements",
                        "severity": "High",
                    }
                )

            # Test session management
            if not self._check_session_security():
                self.results["high_issues"].append(
                    {
                        "category": "Authentication",
                        "issue": "Insecure session management",
                        "description": "Session tokens may not be properly secured",
                        "severity": "High",
                    }
                )

        except Exception as e:
            logger.error(f"Authentication audit failed: {e}")

    def _audit_authorization(self):
        """Audit authorization mechanisms"""
        logger.info("Auditing authorization...")

        try:
            # Test privilege escalation
            test_endpoints = [
                "/api/v1/users/",
                "/api/v1/admin/",
                "/api/v1/monitoring/",
                "/api/v1/security/",
            ]

            for endpoint in test_endpoints:
                response = requests.get(f"http://localhost:8001{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.results["high_issues"].append(
                        {
                            "category": "Authorization",
                            "issue": "Unauthorized access",
                            "description": f"Endpoint {endpoint} accessible without authentication",
                            "severity": "High",
                        }
                    )

            # Test role-based access control
            if not self._check_rbac():
                self.results["medium_issues"].append(
                    {
                        "category": "Authorization",
                        "issue": "RBAC not properly implemented",
                        "description": "Role-based access control may have gaps",
                        "severity": "Medium",
                    }
                )

        except Exception as e:
            logger.error(f"Authorization audit failed: {e}")

    def _audit_input_validation(self):
        """Audit input validation"""
        logger.info("Auditing input validation...")

        try:
            # Test SQL injection
            sql_payloads = [
                "'; DROP TABLE users; --",
                "' OR '1'='1",
                "'; INSERT INTO users VALUES ('hacker', 'password'); --",
            ]

            for payload in sql_payloads:
                response = requests.post(
                    "http://localhost:8001/api/v1/auth/register",
                    json={
                        "username": payload,
                        "email": "test@test.com",
                        "password": "password",
                    },
                    timeout=5,
                )
                if "error" not in response.text.lower() and response.status_code == 200:
                    self.results["critical_issues"].append(
                        {
                            "category": "Input Validation",
                            "issue": "SQL injection vulnerability",
                            "description": f'SQL payload "{payload}" was accepted',
                            "severity": "Critical",
                        }
                    )

            # Test XSS
            xss_payloads = [
                '<script>alert("XSS")</script>',
                'javascript:alert("XSS")',
                '<img src=x onerror=alert("XSS")>',
            ]

            for payload in xss_payloads:
                response = requests.post(
                    "http://localhost:8001/api/v1/users/",
                    json={"username": payload, "email": "test@test.com"},
                    timeout=5,
                )
                if payload in response.text:
                    self.results["high_issues"].append(
                        {
                            "category": "Input Validation",
                            "issue": "XSS vulnerability",
                            "description": f'XSS payload "{payload}" was reflected',
                            "severity": "High",
                        }
                    )

        except Exception as e:
            logger.error(f"Input validation audit failed: {e}")

    def _audit_sql_injection(self):
        """Audit SQL injection vulnerabilities"""
        logger.info("Auditing SQL injection...")

        try:
            # Test database connection
            db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'nexus')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'nexus')}"
            engine = create_engine(db_url)

            with engine.connect() as conn:
                # Test for SQL injection in user queries
                result = conn.execute(
                    text("SELECT * FROM users WHERE username = 'admin' OR '1'='1'")
                )
                if result.rowcount > 0:
                    self.results["critical_issues"].append(
                        {
                            "category": "SQL Injection",
                            "issue": "SQL injection vulnerability",
                            "description": "Database queries may be vulnerable to SQL injection",
                            "severity": "Critical",
                        }
                    )

        except Exception as e:
            logger.error(f"SQL injection audit failed: {e}")

    def _audit_xss_protection(self):
        """Audit XSS protection"""
        logger.info("Auditing XSS protection...")

        try:
            # Check for XSS protection headers
            response = requests.get("http://localhost:8001/", timeout=5)
            headers = response.headers

            if "X-XSS-Protection" not in headers:
                self.results["medium_issues"].append(
                    {
                        "category": "XSS Protection",
                        "issue": "Missing XSS protection header",
                        "description": "X-XSS-Protection header not set",
                        "severity": "Medium",
                    }
                )

            if "Content-Security-Policy" not in headers:
                self.results["medium_issues"].append(
                    {
                        "category": "XSS Protection",
                        "issue": "Missing CSP header",
                        "description": "Content Security Policy header not set",
                        "severity": "Medium",
                    }
                )

        except Exception as e:
            logger.error(f"XSS protection audit failed: {e}")

    def _audit_csrf_protection(self):
        """Audit CSRF protection"""
        logger.info("Auditing CSRF protection...")

        try:
            # Test CSRF protection
            response = requests.post(
                "http://localhost:8001/api/v1/users/",
                json={"username": "test", "email": "test@test.com"},
                timeout=5,
            )

            if response.status_code == 200:
                self.results["high_issues"].append(
                    {
                        "category": "CSRF Protection",
                        "issue": "Missing CSRF protection",
                        "description": "POST requests may be vulnerable to CSRF attacks",
                        "severity": "High",
                    }
                )

        except Exception as e:
            logger.error(f"CSRF protection audit failed: {e}")

    def _audit_ssl_tls(self):
        """Audit SSL/TLS configuration"""
        logger.info("Auditing SSL/TLS...")

        try:
            # Test HTTPS endpoint
            response = requests.get("https://localhost:443/", verify=False, timeout=5)

            if response.status_code == 200:
                # Check SSL certificate
                if not self._check_ssl_certificate():
                    self.results["high_issues"].append(
                        {
                            "category": "SSL/TLS",
                            "issue": "SSL certificate issues",
                            "description": "SSL certificate may have issues",
                            "severity": "High",
                        }
                    )
            else:
                self.results["critical_issues"].append(
                    {
                        "category": "SSL/TLS",
                        "issue": "HTTPS not available",
                        "description": "HTTPS endpoint not accessible",
                        "severity": "Critical",
                    }
                )

        except Exception as e:
            logger.error(f"SSL/TLS audit failed: {e}")

    def _audit_security_headers(self):
        """Audit security headers"""
        logger.info("Auditing security headers...")

        try:
            response = requests.get("http://localhost:8001/", timeout=5)
            headers = response.headers

            required_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "Strict-Transport-Security": "max-age=31536000",
                "Referrer-Policy": "strict-origin-when-cross-origin",
            }

            for header, expected_value in required_headers.items():
                if header not in headers:
                    self.results["medium_issues"].append(
                        {
                            "category": "Security Headers",
                            "issue": f"Missing {header} header",
                            "description": f"Security header {header} not set",
                            "severity": "Medium",
                        }
                    )

        except Exception as e:
            logger.error(f"Security headers audit failed: {e}")

    def _audit_rate_limiting(self):
        """Audit rate limiting"""
        logger.info("Auditing rate limiting...")

        try:
            # Test rate limiting
            for i in range(100):
                response = requests.get("http://localhost:8001/api/v1/", timeout=5)
                if response.status_code == 429:
                    break
            else:
                self.results["medium_issues"].append(
                    {
                        "category": "Rate Limiting",
                        "issue": "Rate limiting not working",
                        "description": "Rate limiting may not be properly configured",
                        "severity": "Medium",
                    }
                )

        except Exception as e:
            logger.error(f"Rate limiting audit failed: {e}")

    def _audit_file_uploads(self):
        """Audit file upload security"""
        logger.info("Auditing file uploads...")

        try:
            # Test file upload restrictions
            test_files = [
                ("test.php", '<?php echo "test"; ?>'),
                ("test.jsp", '<% out.println("test"); %>'),
                ("test.exe", b"\x4d\x5a\x90\x00"),
            ]

            for filename, content in test_files:
                files = {"file": (filename, content)}
                response = requests.post(
                    "http://localhost:8001/api/v1/upload", files=files, timeout=5
                )

                if response.status_code == 200:
                    self.results["high_issues"].append(
                        {
                            "category": "File Upload",
                            "issue": "Unrestricted file upload",
                            "description": f"Dangerous file type {filename} was accepted",
                            "severity": "High",
                        }
                    )

        except Exception as e:
            logger.error(f"File upload audit failed: {e}")

    def _audit_api_security(self):
        """Audit API security"""
        logger.info("Auditing API security...")

        try:
            # Test API versioning
            response = requests.get("http://localhost:8001/api/v1/", timeout=5)
            if response.status_code != 200:
                self.results["low_issues"].append(
                    {
                        "category": "API Security",
                        "issue": "API versioning issues",
                        "description": "API versioning may not be properly implemented",
                        "severity": "Low",
                    }
                )

            # Test API documentation
            response = requests.get("http://localhost:8001/docs", timeout=5)
            if response.status_code == 200:
                self.results["low_issues"].append(
                    {
                        "category": "API Security",
                        "issue": "API documentation exposed",
                        "description": "API documentation may expose sensitive information",
                        "severity": "Low",
                    }
                )

        except Exception as e:
            logger.error(f"API security audit failed: {e}")

    def _audit_database_security(self):
        """Audit database security"""
        logger.info("Auditing database security...")

        try:
            # Test database connection security
            db_url = f"postgresql://{os.getenv('POSTGRES_USER', 'nexus')}:{os.getenv('POSTGRES_PASSWORD', 'password')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'nexus')}"

            if "password" in db_url.lower():
                self.results["critical_issues"].append(
                    {
                        "category": "Database Security",
                        "issue": "Weak database password",
                        "description": "Database password appears to be weak",
                        "severity": "Critical",
                    }
                )

            # Test Redis security
            redis_client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379")),
            )
            redis_client.ping()

            if not redis_client.config_get("requirepass"):
                self.results["high_issues"].append(
                    {
                        "category": "Database Security",
                        "issue": "Redis not password protected",
                        "description": "Redis instance may not be password protected",
                        "severity": "High",
                    }
                )

        except Exception as e:
            logger.error(f"Database security audit failed: {e}")

    def _audit_docker_security(self):
        """Audit Docker security"""
        logger.info("Auditing Docker security...")

        try:
            # Test Docker daemon security
            client = docker.from_env()
            containers = client.containers.list()

            for container in containers:
                # Check if containers are running as root
                if container.attrs["Config"]["User"] == "":
                    self.results["high_issues"].append(
                        {
                            "category": "Docker Security",
                            "issue": "Container running as root",
                            "description": f"Container {container.name} is running as root",
                            "severity": "High",
                        }
                    )

                # Check for privileged containers
                if container.attrs["HostConfig"]["Privileged"]:
                    self.results["critical_issues"].append(
                        {
                            "category": "Docker Security",
                            "issue": "Privileged container",
                            "description": f"Container {container.name} is running in privileged mode",
                            "severity": "Critical",
                        }
                    )

        except DockerException as e:
            logger.error(f"Docker security audit failed: {e}")

    def _audit_infrastructure_security(self):
        """Audit infrastructure security"""
        logger.info("Auditing infrastructure security...")

        try:
            # Check for exposed ports
            exposed_ports = [8001, 3000, 5432, 6379, 9090]

            for port in exposed_ports:
                response = requests.get(f"http://localhost:{port}", timeout=2)
                if response.status_code == 200:
                    self.results["medium_issues"].append(
                        {
                            "category": "Infrastructure Security",
                            "issue": f"Port {port} exposed",
                            "description": f"Port {port} is accessible from outside",
                            "severity": "Medium",
                        }
                    )

        except Exception as e:
            logger.error(f"Infrastructure security audit failed: {e}")

    def _check_password_policy(self) -> bool:
        """Check password policy implementation"""
        # This would check if password complexity requirements are enforced
        return False  # Placeholder

    def _check_session_security(self) -> bool:
        """Check session security implementation"""
        # This would check if sessions are properly secured
        return False  # Placeholder

    def _check_rbac(self) -> bool:
        """Check role-based access control implementation"""
        # This would check if RBAC is properly implemented
        return False  # Placeholder

    def _check_ssl_certificate(self) -> bool:
        """Check SSL certificate validity"""
        # This would check SSL certificate validity
        return False  # Placeholder

    def _calculate_security_score(self):
        """Calculate overall security score"""
        total_issues = (
            len(self.results["critical_issues"])
            + len(self.results["high_issues"])
            + len(self.results["medium_issues"])
            + len(self.results["low_issues"])
        )

        if total_issues == 0:
            self.results["overall_score"] = 100
        else:
            # Weight issues by severity
            critical_weight = len(self.results["critical_issues"]) * 10
            high_weight = len(self.results["high_issues"]) * 5
            medium_weight = len(self.results["medium_issues"]) * 2
            low_weight = len(self.results["low_issues"]) * 1

            total_weight = critical_weight + high_weight + medium_weight + low_weight
            self.results["overall_score"] = max(0, 100 - total_weight)

    def _generate_recommendations(self):
        """Generate security recommendations"""
        recommendations = []

        if self.results["critical_issues"]:
            recommendations.append("Address all critical security issues immediately")

        if self.results["high_issues"]:
            recommendations.append("Implement proper authentication and authorization")
            recommendations.append("Enable HTTPS and SSL/TLS")
            recommendations.append("Implement input validation and sanitization")

        if self.results["medium_issues"]:
            recommendations.append("Add security headers")
            recommendations.append("Implement rate limiting")
            recommendations.append("Secure file uploads")

        if self.results["low_issues"]:
            recommendations.append("Review API documentation exposure")
            recommendations.append("Implement proper logging and monitoring")

        self.results["recommendations"] = recommendations


def main():
    """Main function for security audit"""
    import argparse

    parser = argparse.ArgumentParser(description="NEXUS Platform Security Audit")
    parser.add_argument("--output", type=str, help="Output file for audit results")
    parser.add_argument(
        "--format", choices=["json", "yaml"], default="json", help="Output format"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Load configuration
    config = {"target_url": "http://localhost:8001", "timeout": 5}

    # Initialize security audit
    audit = SecurityAudit(config)

    # Run audit
    results = audit.run_full_audit()

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            if args.format == "json":
                json.dump(results, f, indent=2)
            else:
                yaml.dump(results, f, default_flow_style=False)
    else:
        print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
