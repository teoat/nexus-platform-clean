#!/usr/bin/env python3
"""
NEXUS Platform - Comprehensive Load Testing Script
Production-scale load testing with Locust and custom scenarios
"""

import asyncio
import json
import logging
import os
import statistics
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Test result data structure"""

    test_name: str
    success: bool
    response_time: float
    status_code: int
    error_message: Optional[str] = None
    timestamp: str = None


class LoadTester:
    """Comprehensive load testing for NEXUS Platform"""

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        frontend_url: str = "http://localhost:3000",
    ):
        self.base_url = base_url
        self.frontend_url = frontend_url
        self.results: List[TestResult] = []
        self.session = requests.Session()
        self.auth_token = None

    def authenticate(
        self, username: str = "testuser", password: str = "testpassword"
    ) -> bool:
        """Authenticate and get JWT token"""
        try:
            # Register user first
            register_data = {
                "username": username,
                "email": f"{username}@test.com",
                "password": password,
            }

            response = self.session.post(
                f"{self.base_url}/api/v1/auth/register", json=register_data
            )
            if response.status_code not in [200, 201]:
                logger.warning(f"User registration failed: {response.status_code}")

            # Login
            login_data = {"username": username, "password": password}

            response = self.session.post(
                f"{self.base_url}/api/v1/auth/token", data=login_data
            )
            if response.status_code == 200:
                self.auth_token = response.json().get("access_token")
                self.session.headers.update(
                    {"Authorization": f"Bearer {self.auth_token}"}
                )
                logger.info("Authentication successful")
                return True
            else:
                logger.error(f"Authentication failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

    def test_health_endpoint(self) -> TestResult:
        """Test health endpoint"""
        start_time = time.time()
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response_time = time.time() - start_time

            return TestResult(
                test_name="health_check",
                success=response.status_code == 200,
                response_time=response_time,
                status_code=response.status_code,
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            return TestResult(
                test_name="health_check",
                success=False,
                response_time=time.time() - start_time,
                status_code=0,
                error_message=str(e),
                timestamp=datetime.now().isoformat(),
            )

    def test_api_endpoints(self) -> List[TestResult]:
        """Test various API endpoints"""
        endpoints = [
            ("/api/v1/", "GET"),
            ("/api/v1/users/me", "GET"),
            ("/api/v1/accounts", "GET"),
            ("/api/v1/transactions", "GET"),
            ("/api/v1/monitoring/metrics", "GET"),
        ]

        results = []
        for endpoint, method in endpoints:
            start_time = time.time()
            try:
                if method == "GET":
                    response = self.session.get(
                        f"{self.base_url}{endpoint}", timeout=10
                    )
                else:
                    response = self.session.post(
                        f"{self.base_url}{endpoint}", timeout=10
                    )

                response_time = time.time() - start_time

                results.append(
                    TestResult(
                        test_name=f"api_{endpoint.replace('/', '_').replace('api_v1_', '')}",
                        success=response.status_code
                        in [200, 201, 404],  # 404 is acceptable for some endpoints
                        response_time=response_time,
                        status_code=response.status_code,
                        timestamp=datetime.now().isoformat(),
                    )
                )

            except Exception as e:
                results.append(
                    TestResult(
                        test_name=f"api_{endpoint.replace('/', '_').replace('api_v1_', '')}",
                        success=False,
                        response_time=time.time() - start_time,
                        status_code=0,
                        error_message=str(e),
                        timestamp=datetime.now().isoformat(),
                    )
                )

        return results

    def test_frontend_endpoints(self) -> List[TestResult]:
        """Test frontend endpoints"""
        endpoints = [
            "/",
            "/login",
            "/register",
            "/dashboard",
            "/accounts",
            "/transactions",
            "/analytics",
        ]

        results = []
        for endpoint in endpoints:
            start_time = time.time()
            try:
                response = self.session.get(
                    f"{self.frontend_url}{endpoint}", timeout=10
                )
                response_time = time.time() - start_time

                results.append(
                    TestResult(
                        test_name=f"frontend_{endpoint.replace('/', '_') or 'root'}",
                        success=response.status_code == 200,
                        response_time=response_time,
                        status_code=response.status_code,
                        timestamp=datetime.now().isoformat(),
                    )
                )

            except Exception as e:
                results.append(
                    TestResult(
                        test_name=f"frontend_{endpoint.replace('/', '_') or 'root'}",
                        success=False,
                        response_time=time.time() - start_time,
                        status_code=0,
                        error_message=str(e),
                        timestamp=datetime.now().isoformat(),
                    )
                )

        return results

    def test_concurrent_requests(
        self, num_requests: int = 100, num_threads: int = 10
    ) -> List[TestResult]:
        """Test concurrent requests"""
        results = []

        def make_request(request_id: int) -> TestResult:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}/health", timeout=10)
                response_time = time.time() - start_time

                return TestResult(
                    test_name=f"concurrent_request_{request_id}",
                    success=response.status_code == 200,
                    response_time=response_time,
                    status_code=response.status_code,
                    timestamp=datetime.now().isoformat(),
                )
            except Exception as e:
                return TestResult(
                    test_name=f"concurrent_request_{request_id}",
                    success=False,
                    response_time=time.time() - start_time,
                    status_code=0,
                    error_message=str(e),
                    timestamp=datetime.now().isoformat(),
                )

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(make_request, i) for i in range(num_requests)]

            for future in as_completed(futures):
                results.append(future.result())

        return results

    def test_stress_load(
        self, duration_seconds: int = 60, requests_per_second: int = 10
    ) -> List[TestResult]:
        """Test stress load for specified duration"""
        results = []
        start_time = time.time()
        request_count = 0

        while time.time() - start_time < duration_seconds:
            batch_start = time.time()

            # Make batch of requests
            batch_results = []
            for _ in range(requests_per_second):
                request_start = time.time()
                try:
                    response = self.session.get(f"{self.base_url}/health", timeout=5)
                    response_time = time.time() - request_start

                    batch_results.append(
                        TestResult(
                            test_name=f"stress_load_{request_count}",
                            success=response.status_code == 200,
                            response_time=response_time,
                            status_code=response.status_code,
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    request_count += 1

                except Exception as e:
                    batch_results.append(
                        TestResult(
                            test_name=f"stress_load_{request_count}",
                            success=False,
                            response_time=time.time() - request_start,
                            status_code=0,
                            error_message=str(e),
                            timestamp=datetime.now().isoformat(),
                        )
                    )
                    request_count += 1

            results.extend(batch_results)

            # Wait for next second
            elapsed = time.time() - batch_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)

        return results

    def run_locust_tests(
        self, users: int = 100, spawn_rate: int = 10, run_time: str = "60s"
    ) -> Dict[str, Any]:
        """Run Locust load tests"""
        try:
            # Create Locust test file
            locust_file = """
from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        # Register and login
        self.register_and_login()

    def register_and_login(self):
        username = f"locust_user_{random.randint(1000, 9999)}"
        password = "locustpassword"
        email = f"{username}@test.com"

        # Register
        self.client.post("/api/v1/auth/register", json={
            "username": username,
            "email": email,
            "password": password
        })

        # Login
        response = self.client.post("/api/v1/auth/token", data={
            "username": username,
            "password": password
        })

        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/")

    @task(2)
    def get_user_info(self):
        self.client.get("/api/v1/users/me")

    @task(1)
    def get_accounts(self):
        self.client.get("/api/v1/accounts")

    @task(1)
    def get_transactions(self):
        self.client.get("/api/v1/transactions")

    @task(1)
    def get_monitoring_metrics(self):
        self.client.get("/api/v1/monitoring/metrics")
"""

            with open("/tmp/locust_test.py", "w") as f:
                f.write(locust_file)

            # Run Locust
            cmd = [
                "locust",
                "-f",
                "/tmp/locust_test.py",
                "--host",
                self.base_url,
                "--users",
                str(users),
                "--spawn-rate",
                str(spawn_rate),
                "--run-time",
                run_time,
                "--headless",
                "--html",
                "/tmp/locust_report.html",
                "--csv",
                "/tmp/locust_stats",
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info("Locust tests completed successfully")
                return {
                    "success": True,
                    "output": result.stdout,
                    "report_file": "/tmp/locust_report.html",
                }
            else:
                logger.error(f"Locust tests failed: {result.stderr}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"Locust test error: {e}")
            return {"success": False, "error": str(e)}

    def analyze_results(self) -> Dict[str, Any]:
        """Analyze test results and generate report"""
        if not self.results:
            return {"error": "No test results to analyze"}

        successful_tests = [r for r in self.results if r.success]
        failed_tests = [r for r in self.results if not r.success]

        response_times = [r.response_time for r in successful_tests]

        analysis = {
            "total_tests": len(self.results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(failed_tests),
            "success_rate": len(successful_tests) / len(self.results) * 100
            if self.results
            else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "avg": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "p95": sorted(response_times)[int(len(response_times) * 0.95)]
                if response_times
                else 0,
                "p99": sorted(response_times)[int(len(response_times) * 0.99)]
                if response_times
                else 0,
            },
            "status_codes": {},
            "errors": [r.error_message for r in failed_tests if r.error_message],
        }

        # Count status codes
        for result in self.results:
            status = result.status_code
            analysis["status_codes"][str(status)] = (
                analysis["status_codes"].get(str(status), 0) + 1
            )

        return analysis

    def save_results(self, filename: str = None) -> str:
        """Save test results to file"""
        if filename is None:
            filename = (
                f"load_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        results_data = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "frontend_url": self.frontend_url,
            "results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "response_time": r.response_time,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "timestamp": r.timestamp,
                }
                for r in self.results
            ],
            "analysis": self.analyze_results(),
        }

        with open(filename, "w") as f:
            json.dump(results_data, f, indent=2)

        logger.info(f"Results saved to {filename}")
        return filename

    def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run comprehensive load testing suite"""
        logger.info("Starting comprehensive load testing...")

        # Authenticate
        if not self.authenticate():
            logger.error("Authentication failed, running tests without auth")

        # Run different test scenarios
        logger.info("Running health endpoint tests...")
        self.results.extend([self.test_health_endpoint() for _ in range(10)])

        logger.info("Running API endpoint tests...")
        self.results.extend(self.test_api_endpoints())

        logger.info("Running frontend endpoint tests...")
        self.results.extend(self.test_frontend_endpoints())

        logger.info("Running concurrent request tests...")
        self.results.extend(self.test_concurrent_requests(100, 20))

        logger.info("Running stress load tests...")
        self.results.extend(self.test_stress_load(30, 20))

        logger.info("Running Locust tests...")
        locust_results = self.run_locust_tests(50, 5, "30s")

        # Analyze results
        analysis = self.analyze_results()
        analysis["locust_results"] = locust_results

        # Save results
        results_file = self.save_results()

        logger.info("Load testing completed!")
        logger.info(f"Total tests: {analysis['total_tests']}")
        logger.info(f"Success rate: {analysis['success_rate']:.2f}%")
        logger.info(f"Average response time: {analysis['response_times']['avg']:.3f}s")

        return analysis


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="NEXUS Platform Load Testing")
    parser.add_argument(
        "--backend-url", default="http://localhost:8001", help="Backend URL"
    )
    parser.add_argument(
        "--frontend-url", default="http://localhost:3000", help="Frontend URL"
    )
    parser.add_argument(
        "--users", type=int, default=50, help="Number of concurrent users for Locust"
    )
    parser.add_argument(
        "--duration", type=int, default=60, help="Test duration in seconds"
    )
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    # Initialize load tester
    tester = LoadTester(args.backend_url, args.frontend_url)

    # Run comprehensive tests
    results = tester.run_comprehensive_tests()

    # Print summary
    print("\n" + "=" * 50)
    print("LOAD TESTING SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {results['total_tests']}")
    print(f"Successful: {results['successful_tests']}")
    print(f"Failed: {results['failed_tests']}")
    print(f"Success Rate: {results['success_rate']:.2f}%")
    print(f"Average Response Time: {results['response_times']['avg']:.3f}s")
    print(f"95th Percentile: {results['response_times']['p95']:.3f}s")
    print(f"99th Percentile: {results['response_times']['p99']:.3f}s")
    print("=" * 50)

    if results["failed_tests"] > 0:
        print(f"\nErrors encountered: {len(results['errors'])}")
        for error in set(results["errors"]):
            print(f"  - {error}")

    return 0 if results["success_rate"] > 95 else 1


if __name__ == "__main__":
    sys.exit(main())
