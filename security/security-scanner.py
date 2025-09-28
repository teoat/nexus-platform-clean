#!/usr/bin/env python3
"""
Advanced Security Scanner for NEXUS Platform - Phase 2 Integration
Comprehensive security scanning and threat detection
"""

import asyncio
import json
import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import requests

import docker

logger = logging.getLogger(__name__)


@dataclass
class SecurityVulnerability:
    target: str
    vulnerability_id: str
    severity: str
    title: str
    description: str
    cve_id: Optional[str]
    cvss_score: Optional[float]
    published_date: Optional[str]
    references: List[str]
    timestamp: str


@dataclass
class SecurityScanResult:
    scan_id: str
    scan_type: str
    target: str
    status: str
    vulnerabilities: List[SecurityVulnerability]
    summary: Dict[str, Any]
    timestamp: str
    duration_seconds: float


class SecurityScanner:
    """Advanced security scanner for containers and infrastructure with AI-enhanced threat detection"""

    def __init__(self):
        self.docker_client = None
        self.trivy_path = "/usr/local/bin/trivy"
        self.nmap_path = "/usr/bin/nmap"
        self.clamav_path = "/usr/bin/clamscan"
        self._initialize_clients()
        self.scan_cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL

        # Initialize ML components for advanced threat detection
        self.threat_model = None
        self.anomaly_detector = None
        self._initialize_ml_components()

    def _initialize_clients(self):
        """Initialize Docker client and security tools"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker client initialized successfully")

            # Check if Trivy is available
            try:
                result = subprocess.run(
                    [self.trivy_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.info(
                        f"Trivy security scanner available: {result.stdout.strip()}"
                    )
                else:
                    logger.warning("Trivy security scanner not available")
            except Exception as e:
                logger.warning(f"Trivy check failed: {e}")

            # Check if Nmap is available
            try:
                result = subprocess.run(
                    [self.nmap_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.info("Nmap network scanner available")
                else:
                    logger.warning("Nmap network scanner not available")
            except Exception as e:
                logger.warning(f"Nmap check failed: {e}")

            # Check if ClamAV is available
            try:
                result = subprocess.run(
                    [self.clamav_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode == 0:
                    logger.info("ClamAV malware scanner available")
                else:
                    logger.warning("ClamAV malware scanner not available")
            except Exception as e:
                logger.warning(f"ClamAV check failed: {e}")

        except Exception as e:
            logger.error(f"Failed to initialize security scanner: {e}")
            self.docker_client = None

    def _train_baseline_models(self):
        """Train baseline ML models with historical security data"""
        try:
            # Generate synthetic training data for demonstration
            # In production, this would use real historical security data
            import numpy as np

            # Create baseline normal behavior data
            np.random.seed(42)
            normal_data = np.random.normal(
                0, 1, (1000, 10)
            )  # 1000 samples, 10 features

            # Add some anomalous data
            anomalous_data = np.random.normal(3, 1, (100, 10))  # 100 anomalous samples

            # Combine and label data
            X = np.vstack([normal_data, anomalous_data])
            y = np.hstack([np.zeros(1000), np.ones(100)])  # 0 = normal, 1 = anomalous

            # Train anomaly detector
            if self.anomaly_detector:
                self.anomaly_detector.fit(X)

            # Train threat classifier
            if self.threat_classifier and self.scaler:
                X_scaled = self.scaler.fit_transform(X)
                self.threat_classifier.fit(X_scaled, y)

            logger.info("Baseline ML models trained successfully")

        except Exception as e:
            logger.warning(f"Failed to train baseline models: {e}")

    def _initialize_ml_components(self):
        """Initialize machine learning components for advanced threat detection"""
        try:
            import numpy as np
            from sklearn.ensemble import (IsolationForest,
                                          RandomForestClassifier)
            from sklearn.preprocessing import StandardScaler

            self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
            self.threat_classifier = RandomForestClassifier(
                n_estimators=100, random_state=42
            )
            self.scaler = StandardScaler()

            # Initialize with baseline training data if available
            self._train_baseline_models()

            logger.info("ML components initialized for advanced threat detection")

        except ImportError as e:
            logger.warning(f"ML libraries not available: {e}")
            self.anomaly_detector = None
            self.threat_classifier = None
            self.scaler = None

    async def scan_container_image(
        self, image_name: str, image_tag: str = "latest"
    ) -> SecurityScanResult:
        """Scan a Docker container image for vulnerabilities"""
        try:
            full_image_name = f"{image_name}:{image_tag}"
            scan_id = f"container_{image_name}_{image_tag}_{int(datetime.utcnow().timestamp())}"

            # Check cache first
            cache_key = f"container_{full_image_name}"
            if self._is_cache_valid(cache_key):
                cached_result = self.scan_cache[cache_key]
                logger.info(f"Using cached scan result for {full_image_name}")
                return cached_result

            start_time = datetime.utcnow()

            # Pull the image if not available locally
            try:
                image = self.docker_client.images.get(full_image_name)
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling image {full_image_name}")
                image = self.docker_client.images.pull(image_name, tag=image_tag)

            # Run Trivy scan
            vulnerabilities = await self._run_trivy_scan(full_image_name)

            # Analyze results
            summary = self._analyze_vulnerabilities(vulnerabilities)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            result = SecurityScanResult(
                scan_id=scan_id,
                scan_type="container_image",
                target=full_image_name,
                status="completed",
                vulnerabilities=vulnerabilities,
                summary=summary,
                timestamp=end_time.isoformat(),
                duration_seconds=duration,
            )

            # Cache the result
            self.scan_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(
                f"Error scanning container image {image_name}:{image_tag}: {e}"
            )
            return SecurityScanResult(
                scan_id=f"error_{int(datetime.utcnow().timestamp())}",
                scan_type="container_image",
                target=f"{image_name}:{image_tag}",
                status="failed",
                vulnerabilities=[],
                summary={"error": str(e)},
                timestamp=datetime.utcnow().isoformat(),
                duration_seconds=0,
            )

    async def scan_running_containers(self) -> List[SecurityScanResult]:
        """Scan all running containers for vulnerabilities"""
        try:
            if not self.docker_client:
                return []

            containers = self.docker_client.containers.list()
            scan_results = []

            for container in containers:
                try:
                    # Get container image
                    image_name = (
                        container.image.tags[0]
                        if container.image.tags
                        else container.image.id
                    )

                    # Scan the container
                    result = await self.scan_container_image(
                        image_name.split(":")[0],
                        image_name.split(":")[1] if ":" in image_name else "latest",
                    )

                    # Add container-specific information
                    result.target = f"{container.name} ({image_name})"
                    result.scan_type = "running_container"

                    scan_results.append(result)

                except Exception as e:
                    logger.error(f"Error scanning container {container.name}: {e}")
                    continue

            return scan_results

        except Exception as e:
            logger.error(f"Error scanning running containers: {e}")
            return []

    async def scan_filesystem(self, path: str) -> SecurityScanResult:
        """Scan filesystem for security issues"""
        try:
            scan_id = f"filesystem_{os.path.basename(path)}_{int(datetime.utcnow().timestamp())}"
            start_time = datetime.utcnow()

            # Check cache first
            cache_key = f"filesystem_{path}"
            if self._is_cache_valid(cache_key):
                cached_result = self.scan_cache[cache_key]
                logger.info(f"Using cached filesystem scan result for {path}")
                return cached_result

            vulnerabilities = []

            # Check for common security issues
            vulnerabilities.extend(await self._check_file_permissions(path))
            vulnerabilities.extend(await self._check_sensitive_files(path))
            vulnerabilities.extend(await self._check_suspicious_patterns(path))

            # Analyze results
            summary = self._analyze_vulnerabilities(vulnerabilities)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            result = SecurityScanResult(
                scan_id=scan_id,
                scan_type="filesystem",
                target=path,
                status="completed",
                vulnerabilities=vulnerabilities,
                summary=summary,
                timestamp=end_time.isoformat(),
                duration_seconds=duration,
            )

            # Cache the result
            self.scan_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(f"Error scanning filesystem {path}: {e}")
            return SecurityScanResult(
                scan_id=f"error_{int(datetime.utcnow().timestamp())}",
                scan_type="filesystem",
                target=path,
                status="failed",
                vulnerabilities=[],
                summary={"error": str(e)},
                timestamp=datetime.utcnow().isoformat(),
                duration_seconds=0,
            )

    async def scan_network_security(
        self, target_host: str, ports: List[int] = None
    ) -> SecurityScanResult:
        """Scan network security for open ports and services with advanced analysis"""
        try:
            scan_id = f"network_{target_host}_{int(datetime.utcnow().timestamp())}"
            start_time = datetime.utcnow()

            vulnerabilities = []

            # Default ports to scan
            if ports is None:
                ports = [22, 80, 443, 8080, 3306, 5432, 6379, 9090]

            # Use Nmap for advanced port scanning if available
            nmap_results = await self._run_nmap_scan(target_host, ports)
            vulnerabilities.extend(nmap_results)

            # Additional security checks
            service_vulns = await self._check_service_vulnerabilities(
                target_host, ports
            )
            vulnerabilities.extend(service_vulns)

            # Analyze results
            summary = self._analyze_vulnerabilities(vulnerabilities)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            return SecurityScanResult(
                scan_id=scan_id,
                scan_type="network",
                target=target_host,
                status="completed",
                vulnerabilities=vulnerabilities,
                summary=summary,
                timestamp=end_time.isoformat(),
                duration_seconds=duration,
            )

        except Exception as e:
            logger.error(f"Error scanning network {target_host}: {e}")
            return SecurityScanResult(
                scan_id=f"error_{int(datetime.utcnow().timestamp())}",
                scan_type="network",
                target=target_host,
                status="failed",
                vulnerabilities=[],
                summary={"error": str(e)},
                timestamp=datetime.utcnow().isoformat(),
                duration_seconds=0,
            )

    async def scan_malware(self, path: str) -> SecurityScanResult:
        """Scan filesystem for malware using ClamAV"""
        try:
            scan_id = (
                f"malware_{os.path.basename(path)}_{int(datetime.utcnow().timestamp())}"
            )
            start_time = datetime.utcnow()

            # Check cache first
            cache_key = f"malware_{path}"
            if self._is_cache_valid(cache_key):
                cached_result = self.scan_cache[cache_key]
                logger.info(f"Using cached malware scan result for {path}")
                return cached_result

            vulnerabilities = []

            # Run ClamAV scan
            clamav_results = await self._run_clamav_scan(path)
            vulnerabilities.extend(clamav_results)

            # Additional malware pattern detection
            pattern_results = await self._check_malware_patterns(path)
            vulnerabilities.extend(pattern_results)

            # Analyze results
            summary = self._analyze_vulnerabilities(vulnerabilities)

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            result = SecurityScanResult(
                scan_id=scan_id,
                scan_type="malware",
                target=path,
                status="completed",
                vulnerabilities=vulnerabilities,
                summary=summary,
                timestamp=end_time.isoformat(),
                duration_seconds=duration,
            )

            # Cache the result
            self.scan_cache[cache_key] = result

            return result

        except Exception as e:
            logger.error(f"Error scanning malware in {path}: {e}")
            return SecurityScanResult(
                scan_id=f"error_{int(datetime.utcnow().timestamp())}",
                scan_type="malware",
                target=path,
                status="failed",
                vulnerabilities=[],
                summary={"error": str(e)},
                timestamp=datetime.utcnow().isoformat(),
                duration_seconds=0,
            )

    async def _run_trivy_scan(self, image_name: str) -> List[SecurityVulnerability]:
        """Run Trivy security scan on container image"""
        try:
            # Run Trivy scan
            cmd = [self.trivy_path, "image", "--format", "json", image_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                logger.error(f"Trivy scan failed: {result.stderr}")
                return []

            # Parse Trivy output
            trivy_data = json.loads(result.stdout)
            vulnerabilities = []

            for result_item in trivy_data.get("Results", []):
                for vuln in result_item.get("Vulnerabilities", []):
                    vulnerabilities.append(
                        SecurityVulnerability(
                            target=image_name,
                            vulnerability_id=vuln.get("VulnerabilityID", ""),
                            severity=vuln.get("Severity", "unknown").lower(),
                            title=vuln.get("Title", ""),
                            description=vuln.get("Description", ""),
                            cve_id=vuln.get("VulnerabilityID"),
                            cvss_score=vuln.get("CVSS", {}).get("nvd", {}).get("Score"),
                            published_date=vuln.get("PublishedDate"),
                            references=vuln.get("References", []),
                            timestamp=datetime.utcnow().isoformat(),
                        )
                    )

            return vulnerabilities

        except Exception as e:
            logger.error(f"Error running Trivy scan: {e}")
            return []

    async def _check_file_permissions(self, path: str) -> List[SecurityVulnerability]:
        """Check file permissions for security issues"""
        vulnerabilities = []

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        stat_info = os.stat(file_path)
                        mode = stat_info.st_mode

                        # Check for world-writable files
                        if mode & 0o002:
                            vulnerabilities.append(
                                SecurityVulnerability(
                                    target=file_path,
                                    vulnerability_id="world_writable_file",
                                    severity="medium",
                                    title="World Writable File",
                                    description=f"File {file_path} is world writable",
                                    cve_id=None,
                                    cvss_score=None,
                                    published_date=None,
                                    references=[],
                                    timestamp=datetime.utcnow().isoformat(),
                                )
                            )

                        # Check for files with SUID/SGID bits
                        if mode & 0o4000 or mode & 0o2000:
                            vulnerabilities.append(
                                SecurityVulnerability(
                                    target=file_path,
                                    vulnerability_id="suid_sgid_file",
                                    severity="high",
                                    title="SUID/SGID File",
                                    description=f"File {file_path} has SUID/SGID bits set",
                                    cve_id=None,
                                    cvss_score=None,
                                    published_date=None,
                                    references=[],
                                    timestamp=datetime.utcnow().isoformat(),
                                )
                            )

                    except (OSError, PermissionError):
                        continue

        except Exception as e:
            logger.error(f"Error checking file permissions: {e}")

        return vulnerabilities

    async def _check_sensitive_files(self, path: str) -> List[SecurityVulnerability]:
        """Check for sensitive files that shouldn't be exposed"""
        vulnerabilities = []
        sensitive_patterns = [
            "*.key",
            "*.pem",
            "*.p12",
            "*.pfx",  # Certificates and keys
            "*.env",
            ".env*",  # Environment files
            "*.sql",
            "*.db",
            "*.sqlite",  # Database files
            "*.log",
            "*.txt",  # Log files
            "id_rsa",
            "id_dsa",
            "known_hosts",  # SSH files
        ]

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)

                    # Check against sensitive patterns
                    for pattern in sensitive_patterns:
                        if file.endswith(pattern.replace("*", "")) or file.startswith(
                            pattern.replace("*", "")
                        ):
                            vulnerabilities.append(
                                SecurityVulnerability(
                                    target=file_path,
                                    vulnerability_id="sensitive_file_exposed",
                                    severity="high",
                                    title="Sensitive File Exposed",
                                    description=f"Sensitive file {file_path} found in filesystem",
                                    cve_id=None,
                                    cvss_score=None,
                                    published_date=None,
                                    references=[],
                                    timestamp=datetime.utcnow().isoformat(),
                                )
                            )
                            break

        except Exception as e:
            logger.error(f"Error checking sensitive files: {e}")

        return vulnerabilities

    async def _check_suspicious_patterns(
        self, path: str
    ) -> List[SecurityVulnerability]:
        """Check for suspicious patterns in files"""
        vulnerabilities = []
        suspicious_patterns = [
            "password",
            "secret",
            "token",
            "api_key",
            "private_key",
            "admin",
            "root",
            "sudo",
            "su -",
            "chmod 777",
        ]

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith((".py", ".js", ".sh", ".conf", ".cfg")):
                        file_path = os.path.join(root, file)
                        try:
                            with open(
                                file_path, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                content = f.read().lower()

                                for pattern in suspicious_patterns:
                                    if pattern in content:
                                        vulnerabilities.append(
                                            SecurityVulnerability(
                                                target=file_path,
                                                vulnerability_id="suspicious_pattern",
                                                severity="low",
                                                title="Suspicious Pattern Found",
                                                description=f"Suspicious pattern '{pattern}' found in {file_path}",
                                                cve_id=None,
                                                cvss_score=None,
                                                published_date=None,
                                                references=[],
                                                timestamp=datetime.utcnow().isoformat(),
                                            )
                                        )
                                        break

                        except (OSError, PermissionError, UnicodeDecodeError):
                            continue

        except Exception as e:
            logger.error(f"Error checking suspicious patterns: {e}")

        return vulnerabilities

    async def _run_nmap_scan(
        self, target_host: str, ports: List[int]
    ) -> List[SecurityVulnerability]:
        """Run Nmap scan for advanced port and service analysis"""
        vulnerabilities = []

        try:
            # Check if Nmap is available
            if not os.path.exists(self.nmap_path):
                # Fallback to basic port checking
                return await self._basic_port_scan(target_host, ports)

            # Run Nmap scan
            port_str = ",".join(map(str, ports))
            cmd = [
                self.nmap_path,
                "-sV",
                "-sC",
                "-O",
                "--script=vuln",
                "-p",
                port_str,
                target_host,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                # Parse Nmap output for vulnerabilities
                vulnerabilities.extend(
                    self._parse_nmap_output(result.stdout, target_host)
                )
            else:
                logger.warning(f"Nmap scan failed: {result.stderr}")
                # Fallback to basic port checking
                return await self._basic_port_scan(target_host, ports)

        except subprocess.TimeoutExpired:
            logger.warning(f"Nmap scan timed out for {target_host}")
            return await self._basic_port_scan(target_host, ports)
        except Exception as e:
            logger.error(f"Nmap scan error: {e}")
            return await self._basic_port_scan(target_host, ports)

        return vulnerabilities

    async def _basic_port_scan(
        self, target_host: str, ports: List[int]
    ) -> List[SecurityVulnerability]:
        """Basic port scanning as fallback"""
        vulnerabilities = []

        for port in ports:
            try:
                result = await self._check_port_open(target_host, port)
                if result["open"]:
                    vulnerabilities.append(
                        SecurityVulnerability(
                            target=f"{target_host}:{port}",
                            vulnerability_id=f"open_port_{port}",
                            severity="medium",
                            title=f"Open Port {port}",
                            description=f"Port {port} is open and accessible",
                            cve_id=None,
                            cvss_score=None,
                            published_date=None,
                            references=[],
                            timestamp=datetime.utcnow().isoformat(),
                        )
                    )
            except Exception as e:
                logger.warning(f"Error checking port {port} on {target_host}: {e}")

        return vulnerabilities

    async def _run_clamav_scan(self, path: str) -> List[SecurityVulnerability]:
        """Run ClamAV malware scan"""
        vulnerabilities = []

        try:
            # Check if ClamAV is available
            if not os.path.exists(self.clamav_path):
                logger.warning("ClamAV not available, skipping malware scan")
                return vulnerabilities

            # Run ClamAV scan
            cmd = [self.clamav_path, "--recursive", "--infected", path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            # Parse ClamAV output
            if result.returncode == 0:
                # No infections found
                pass
            elif result.returncode == 1:
                # Infections found, parse output
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if "FOUND" in line:
                        # Extract file path and malware name
                        parts = line.split(": ")
                        if len(parts) >= 2:
                            file_path = parts[0].strip()
                            malware_name = parts[1].replace(" FOUND", "").strip()

                            vulnerabilities.append(
                                SecurityVulnerability(
                                    target=file_path,
                                    vulnerability_id=f"malware_{hash(malware_name) % 10000}",
                                    severity="critical",
                                    title=f"Malware Detected: {malware_name}",
                                    description=f"Malware {malware_name} found in {file_path}",
                                    cve_id=None,
                                    cvss_score=9.0,
                                    published_date=None,
                                    references=["ClamAV"],
                                    timestamp=datetime.utcnow().isoformat(),
                                )
                            )
            else:
                logger.warning(f"ClamAV scan failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            logger.warning(f"ClamAV scan timed out for {path}")
        except Exception as e:
            logger.error(f"ClamAV scan error: {e}")

        return vulnerabilities

    async def _check_malware_patterns(self, path: str) -> List[SecurityVulnerability]:
        """Check for malware patterns using signature-based detection"""
        vulnerabilities = []

        # Common malware signatures and patterns
        malware_patterns = [
            rb"\x4D\x5A",  # MZ header (Windows executables)
            rb"#!/bin/sh",  # Shell scripts
            rb"<?php",  # PHP webshells
            rb"<script>",  # JavaScript malware
            rb"powershell",  # PowerShell scripts
            rb"eval(",  # JavaScript eval functions
            rb"base64_decode",  # Base64 encoded payloads
        ]

        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # Check file size (skip very large files)
                        if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
                            continue

                        with open(file_path, "rb") as f:
                            # Read first 1KB of file
                            data = f.read(1024)

                            for pattern in malware_patterns:
                                if pattern in data:
                                    vulnerabilities.append(
                                        SecurityVulnerability(
                                            target=file_path,
                                            vulnerability_id=f"pattern_{hash(pattern) % 10000}",
                                            severity="high",
                                            title="Suspicious File Pattern Detected",
                                            description=f"Suspicious pattern found in {file_path}",
                                            cve_id=None,
                                            cvss_score=7.0,
                                            published_date=None,
                                            references=["Pattern Analysis"],
                                            timestamp=datetime.utcnow().isoformat(),
                                        )
                                    )
                                    break  # Only report once per file

                    except (OSError, PermissionError):
                        continue

        except Exception as e:
            logger.error(f"Error checking malware patterns: {e}")

        return vulnerabilities

    async def _check_service_vulnerabilities(
        self, target_host: str, ports: List[int]
    ) -> List[SecurityVulnerability]:
        """Check for known service vulnerabilities"""
        vulnerabilities = []

        # Common service vulnerability checks
        service_checks = {
            22: self._check_ssh_vulnerabilities,
            80: self._check_http_vulnerabilities,
            443: self._check_https_vulnerabilities,
            3306: self._check_mysql_vulnerabilities,
            5432: self._check_postgres_vulnerabilities,
        }

        for port in ports:
            if port in service_checks:
                try:
                    port_vulns = await service_checks[port](target_host, port)
                    vulnerabilities.extend(port_vulns)
                except Exception as e:
                    logger.warning(f"Error checking service on port {port}: {e}")

        return vulnerabilities

    async def _check_ssh_vulnerabilities(
        self, host: str, port: int
    ) -> List[SecurityVulnerability]:
        """Check SSH service for vulnerabilities"""
        vulnerabilities = []

        # Check for weak SSH configurations
        # This is a simplified check - in production, use specialized SSH scanners
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                # SSH is running, check for common vulnerabilities
                vulnerabilities.append(
                    SecurityVulnerability(
                        target=f"{host}:{port}",
                        vulnerability_id="ssh_running",
                        severity="low",
                        title="SSH Service Running",
                        description="SSH service is accessible - ensure proper key-based authentication",
                        cve_id=None,
                        cvss_score=3.0,
                        published_date=None,
                        references=["SSH Security Best Practices"],
                        timestamp=datetime.utcnow().isoformat(),
                    )
                )
        except Exception as e:
            pass

        return vulnerabilities

    async def _check_http_vulnerabilities(
        self, host: str, port: int
    ) -> List[SecurityVulnerability]:
        """Check HTTP service for vulnerabilities"""
        vulnerabilities = []

        try:
            import requests

            url = f"http://{host}:{port}"
            response = requests.get(url, timeout=10, verify=False)

            # Check for common HTTP vulnerabilities
            if "server" in response.headers:
                server = response.headers["server"].lower()
                if "apache" in server and "2.4" not in server:
                    vulnerabilities.append(
                        SecurityVulnerability(
                            target=f"{host}:{port}",
                            vulnerability_id="old_apache",
                            severity="medium",
                            title="Potentially Outdated Apache Server",
                            description=f"Apache server version may be outdated: {response.headers['server']}",
                            cve_id=None,
                            cvss_score=5.0,
                            published_date=None,
                            references=["Apache Security"],
                            timestamp=datetime.utcnow().isoformat(),
                        )
                    )

        except Exception as e:
            pass

        return vulnerabilities

    async def _check_https_vulnerabilities(
        self, host: str, port: int
    ) -> List[SecurityVulnerability]:
        """Check HTTPS service for vulnerabilities"""
        vulnerabilities = []

        try:
            import socket
            import ssl

            context = ssl.create_default_context()
            with socket.create_connection((host, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert = ssock.getpeercert()

                    # Check certificate validity
                    import datetime

                    not_after = datetime.datetime.strptime(
                        cert["notAfter"], "%b %d %H:%M:%S %Y %Z"
                    )
                    if not_after < datetime.datetime.now():
                        vulnerabilities.append(
                            SecurityVulnerability(
                                target=f"{host}:{port}",
                                vulnerability_id="expired_cert",
                                severity="high",
                                title="Expired SSL Certificate",
                                description="SSL certificate has expired",
                                cve_id=None,
                                cvss_score=7.0,
                                published_date=None,
                                references=["SSL Certificate Validation"],
                                timestamp=datetime.utcnow().isoformat(),
                            )
                        )

        except Exception as e:
            pass

        return vulnerabilities

    async def _check_mysql_vulnerabilities(
        self, host: str, port: int
    ) -> List[SecurityVulnerability]:
        """Check MySQL service for vulnerabilities"""
        vulnerabilities = []

        # Check if MySQL is accessible without authentication
        try:
            import mysql.connector

            conn = mysql.connector.connect(host=host, port=port, connect_timeout=5)
            conn.close()

            vulnerabilities.append(
                SecurityVulnerability(
                    target=f"{host}:{port}",
                    vulnerability_id="mysql_open",
                    severity="critical",
                    title="MySQL Accessible Without Authentication",
                    description="MySQL service is accessible without authentication",
                    cve_id=None,
                    cvss_score=9.0,
                    published_date=None,
                    references=["MySQL Security"],
                    timestamp=datetime.utcnow().isoformat(),
                )
            )

        except Exception as e:
            pass

        return vulnerabilities

    async def _check_postgres_vulnerabilities(
        self, host: str, port: int
    ) -> List[SecurityVulnerability]:
        """Check PostgreSQL service for vulnerabilities"""
        vulnerabilities = []

        # Check if PostgreSQL is accessible without authentication
        try:
            import psycopg2

            conn = psycopg2.connect(host=host, port=port, connect_timeout=5)
            conn.close()

            vulnerabilities.append(
                SecurityVulnerability(
                    target=f"{host}:{port}",
                    vulnerability_id="postgres_open",
                    severity="critical",
                    title="PostgreSQL Accessible Without Authentication",
                    description="PostgreSQL service is accessible without authentication",
                    cve_id=None,
                    cvss_score=9.0,
                    published_date=None,
                    references=["PostgreSQL Security"],
                    timestamp=datetime.utcnow().isoformat(),
                )
            )

        except Exception as e:
            pass

        return vulnerabilities

    def _parse_nmap_output(
        self, output: str, target_host: str
    ) -> List[SecurityVulnerability]:
        """Parse Nmap output for vulnerabilities"""
        vulnerabilities = []

        lines = output.split("\n")
        for line in lines:
            # Look for vulnerability information in Nmap output
            if "VULNERABLE" in line or "vulnerable" in line.lower():
                vulnerabilities.append(
                    SecurityVulnerability(
                        target=target_host,
                        vulnerability_id=f"nmap_vuln_{hash(line) % 10000}",
                        severity="high",
                        title="Nmap Detected Vulnerability",
                        description=f"Nmap scan detected: {line.strip()}",
                        cve_id=None,
                        cvss_score=7.0,
                        published_date=None,
                        references=["Nmap Scan"],
                        timestamp=datetime.utcnow().isoformat(),
                    )
                )

        return vulnerabilities

    async def _check_port_open(self, host: str, port: int) -> Dict[str, Any]:
        """Check if a port is open on a host"""
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()

            return {"host": host, "port": port, "open": result == 0}
        except Exception as e:
            return {"host": host, "port": port, "open": False, "error": str(e)}

    def _analyze_vulnerabilities(
        self, vulnerabilities: List[SecurityVulnerability]
    ) -> Dict[str, Any]:
        """Analyze vulnerabilities and create summary with ML-enhanced risk assessment"""
        if not vulnerabilities:
            return {
                "total_vulnerabilities": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "unknown": 0,
                "risk_score": 0,
                "ml_risk_score": 0,
                "threat_probability": 0.0,
            }

        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "unknown": 0,
        }

        for vuln in vulnerabilities:
            severity = vuln.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
            else:
                severity_counts["unknown"] += 1

        # Calculate traditional risk score (weighted by severity)
        risk_score = (
            severity_counts["critical"] * 10
            + severity_counts["high"] * 7
            + severity_counts["medium"] * 4
            + severity_counts["low"] * 1
            + severity_counts["unknown"] * 2
        )

        # Calculate ML-enhanced risk score
        ml_risk_score = self._calculate_ml_risk_score(vulnerabilities)

        # Calculate threat probability using ML
        threat_probability = self._calculate_threat_probability(vulnerabilities)

        return {
            "total_vulnerabilities": len(vulnerabilities),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"],
            "low": severity_counts["low"],
            "unknown": severity_counts["unknown"],
            "risk_score": risk_score,
            "ml_risk_score": ml_risk_score,
            "threat_probability": threat_probability,
            "risk_level": self._get_risk_level(max(risk_score, ml_risk_score)),
            "ml_enhanced": True,
        }

    def _calculate_ml_risk_score(
        self, vulnerabilities: List[SecurityVulnerability]
    ) -> int:
        """Calculate ML-enhanced risk score based on vulnerability patterns"""
        if not self.anomaly_detector or not vulnerabilities:
            return 0

        try:
            # Extract features from vulnerabilities
            features = self._extract_vulnerability_features(vulnerabilities)

            if not features:
                return 0

            # Use anomaly detector to assess risk
            import numpy as np

            features_array = np.array([features])

            # Get anomaly score (-1 to 1, where -1 is normal, 1 is anomalous)
            anomaly_score = self.anomaly_detector.decision_function(features_array)[0]

            # Convert to risk score (0-100)
            # Higher anomaly score = higher risk
            risk_score = int((anomaly_score + 1) * 50)

            return max(0, min(100, risk_score))

        except Exception as e:
            logger.warning(f"ML risk score calculation failed: {e}")
            return 0

    def _calculate_threat_probability(
        self, vulnerabilities: List[SecurityVulnerability]
    ) -> float:
        """Calculate probability of active threat using ML classification"""
        if not self.threat_classifier or not self.scaler or not vulnerabilities:
            return 0.0

        try:
            # Extract features from vulnerabilities
            features = self._extract_vulnerability_features(vulnerabilities)

            if not features:
                return 0.0

            # Scale features and predict threat probability
            import numpy as np

            features_array = np.array([features])
            features_scaled = self.scaler.transform(features_array)

            # Get threat probability (0-1)
            threat_prob = self.threat_classifier.predict_proba(features_scaled)[0][1]

            return float(threat_prob)

        except Exception as e:
            logger.warning(f"Threat probability calculation failed: {e}")
            return 0.0

    def _extract_vulnerability_features(
        self, vulnerabilities: List[SecurityVulnerability]
    ) -> List[float]:
        """Extract numerical features from vulnerabilities for ML analysis"""
        if not vulnerabilities:
            return []

        features = []

        # Count vulnerabilities by severity
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "unknown": 0,
        }
        for vuln in vulnerabilities:
            severity = vuln.severity.lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
            else:
                severity_counts["unknown"] += 1

        # Add severity counts as features
        features.extend(
            [
                severity_counts["critical"],
                severity_counts["high"],
                severity_counts["medium"],
                severity_counts["low"],
                severity_counts["unknown"],
            ]
        )

        # Add CVSS scores (average and max)
        cvss_scores = [
            v.cvss_score for v in vulnerabilities if v.cvss_score is not None
        ]
        if cvss_scores:
            features.extend(
                [
                    sum(cvss_scores) / len(cvss_scores),  # Average CVSS
                    max(cvss_scores),  # Max CVSS
                    min(cvss_scores),  # Min CVSS
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0])

        # Add vulnerability age (days since published)
        from datetime import datetime

        current_time = datetime.utcnow()
        ages = []
        for vuln in vulnerabilities:
            if vuln.published_date:
                try:
                    published = datetime.fromisoformat(
                        vuln.published_date.replace("Z", "+00:00")
                    )
                    age_days = (current_time - published).days
                    ages.append(age_days)
                except:
                    pass

        if ages:
            features.extend(
                [
                    sum(ages) / len(ages),  # Average age
                    max(ages),  # Max age
                    min(ages),  # Min age
                ]
            )
        else:
            features.extend([0.0, 0.0, 0.0])

        # Add total count and unique targets
        features.append(len(vulnerabilities))
        unique_targets = len(set(v.target for v in vulnerabilities))
        features.append(unique_targets)

        return features

    def _get_risk_level(self, risk_score: int) -> str:
        """Get risk level based on score"""
        if risk_score >= 50:
            return "critical"
        elif risk_score >= 30:
            return "high"
        elif risk_score >= 15:
            return "medium"
        elif risk_score >= 5:
            return "low"
        else:
            return "minimal"

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        if cache_key not in self.scan_cache:
            return False

        cached_time = datetime.fromisoformat(self.scan_cache[cache_key].timestamp)
        return (datetime.utcnow() - cached_time).total_seconds() < self.cache_ttl

    async def get_security_summary(self) -> Dict[str, Any]:
        """Get overall security summary with ML-enhanced analysis"""
        try:
            # Get recent scan results
            recent_scans = []
            cutoff_time = datetime.utcnow() - timedelta(hours=24)

            for cache_key, result in self.scan_cache.items():
                scan_time = datetime.fromisoformat(result.timestamp)
                if scan_time > cutoff_time:
                    recent_scans.append(result)

            # Analyze overall security posture
            total_vulnerabilities = sum(
                len(scan.vulnerabilities) for scan in recent_scans
            )
            critical_vulnerabilities = sum(
                len([v for v in scan.vulnerabilities if v.severity == "critical"])
                for scan in recent_scans
            )

            # Calculate ML-enhanced metrics
            ml_risk_scores = [
                scan.summary.get("ml_risk_score", 0)
                for scan in recent_scans
                if scan.summary.get("ml_enhanced")
            ]
            avg_ml_risk = (
                sum(ml_risk_scores) / len(ml_risk_scores) if ml_risk_scores else 0
            )

            threat_probabilities = [
                scan.summary.get("threat_probability", 0.0)
                for scan in recent_scans
                if scan.summary.get("ml_enhanced")
            ]
            avg_threat_prob = (
                sum(threat_probabilities) / len(threat_probabilities)
                if threat_probabilities
                else 0.0
            )

            # Calculate overall security score
            traditional_score = max(
                0, 100 - (critical_vulnerabilities * 10 + total_vulnerabilities)
            )
            ml_adjusted_score = max(
                0, 100 - int(avg_ml_risk * 2) - int(avg_threat_prob * 100)
            )

            return {
                "total_scans_24h": len(recent_scans),
                "total_vulnerabilities": total_vulnerabilities,
                "critical_vulnerabilities": critical_vulnerabilities,
                "security_score": traditional_score,
                "ml_enhanced_score": ml_adjusted_score,
                "average_ml_risk": avg_ml_risk,
                "average_threat_probability": avg_threat_prob,
                "ml_coverage": len(
                    [s for s in recent_scans if s.summary.get("ml_enhanced")]
                )
                / max(1, len(recent_scans)),
                "last_scan": max([scan.timestamp for scan in recent_scans])
                if recent_scans
                else None,
                "recommendations": self._get_security_recommendations(recent_scans),
                "scan_types": list(set(scan.scan_type for scan in recent_scans)),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error getting security summary: {e}")
            return {"error": str(e)}

    def _get_security_recommendations(
        self, scans: List[SecurityScanResult]
    ) -> List[str]:
        """Get security recommendations based on scan results"""
        recommendations = []

        critical_count = sum(
            len([v for v in scan.vulnerabilities if v.severity == "critical"])
            for scan in scans
        )

        if critical_count > 0:
            recommendations.append(
                f"Address {critical_count} critical vulnerabilities immediately"
            )

        # Check for common issues
        world_writable_files = sum(
            len(
                [
                    v
                    for v in scan.vulnerabilities
                    if v.vulnerability_id == "world_writable_file"
                ]
            )
            for scan in scans
        )

        if world_writable_files > 0:
            recommendations.append(f"Fix {world_writable_files} world-writable files")

        # General recommendations
        if not recommendations:
            recommendations.append("Continue regular security scanning")
            recommendations.append("Keep container images updated")
            recommendations.append("Review and update security policies")

        return recommendations


# Global security scanner instance
security_scanner = SecurityScanner()
