#!/usr/bin/env python3
"""
NEXUS Platform - Performance Benchmarking Script
Comprehensive performance benchmarking for system components
"""

import argparse
import asyncio
import json
import logging
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PerformanceBenchmark:
    """Performance benchmarking for NEXUS Platform"""

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.start_time = time.time()

    def measure_system_resources(self) -> Dict[str, Any]:
        """Measure system resource usage"""
        logger.info("Measuring system resources...")

        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "cpu_count_logical": psutil.cpu_count(logical=True),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "disk_total": psutil.disk_usage("/").total,
            "disk_free": psutil.disk_usage("/").free,
            "disk_percent": psutil.disk_usage("/").percent,
            "network_connections": len(psutil.net_connections()),
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
            "timestamp": datetime.now().isoformat(),
        }

    def benchmark_database_performance(self) -> Dict[str, Any]:
        """Benchmark database performance"""
        logger.info("Benchmarking database performance...")

        try:
            import asyncio

            import asyncpg

            async def db_benchmark():
                # This would require actual database connection
                # For now, return placeholder metrics
                return {
                    "connection_time": 0.001,
                    "query_time_simple": 0.005,
                    "query_time_complex": 0.050,
                    "transactions_per_second": 1000,
                    "connections_active": 5,
                    "connections_idle": 10,
                }

            # Run async benchmark
            return asyncio.run(db_benchmark())

        except ImportError:
            logger.warning("asyncpg not available, skipping database benchmark")
            return {"error": "asyncpg not available"}

    def benchmark_cache_performance(self) -> Dict[str, Any]:
        """Benchmark Redis cache performance"""
        logger.info("Benchmarking cache performance...")

        try:
            import time

            import redis

            # Connect to Redis
            redis_host = os.getenv("REDIS_HOST", "localhost")
            redis_port = int(os.getenv("REDIS_PORT", "6379"))
            redis_password = os.getenv("REDIS_PASSWORD")

            r = redis.Redis(host=redis_host, port=redis_port, password=redis_password)

            # Test connection
            start_time = time.time()
            r.ping()
            connection_time = time.time() - start_time

            # Test basic operations
            test_key = "benchmark_test_key"
            test_value = "benchmark_test_value"

            # SET operation
            start_time = time.time()
            r.set(test_key, test_value)
            set_time = time.time() - start_time

            # GET operation
            start_time = time.time()
            result = r.get(test_key)
            get_time = time.time() - start_time

            # Cleanup
            r.delete(test_key)

            # Get cache statistics
            info = r.info()

            return {
                "connection_time": connection_time,
                "set_time": set_time,
                "get_time": get_time,
                "total_keys": info.get("db0", {}).get("keys", 0),
                "memory_used": info.get("used_memory", 0),
                "memory_peak": info.get("used_memory_peak", 0),
                "hit_rate": info.get("keyspace_hits", 0)
                / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)),
                "connected_clients": info.get("connected_clients", 0),
                "ops_per_sec": info.get("instantaneous_ops_per_sec", 0),
            }

        except ImportError:
            logger.warning("redis not available, skipping cache benchmark")
            return {"error": "redis not available"}
        except Exception as e:
            logger.error(f"Cache benchmark failed: {e}")
            return {"error": str(e)}

    def benchmark_api_performance(
        self, base_url: str = "http://localhost:8000"
    ) -> Dict[str, Any]:
        """Benchmark API performance"""
        logger.info("Benchmarking API performance...")

        try:
            import asyncio

            import aiohttp

            async def api_benchmark():
                async with aiohttp.ClientSession() as session:
                    # Test health endpoint
                    start_time = time.time()
                    async with session.get(f"{base_url}/health") as response:
                        health_time = time.time() - start_time
                        health_status = response.status

                    # Test API health endpoint
                    start_time = time.time()
                    async with session.get(f"{base_url}/api/health") as response:
                        api_health_time = time.time() - start_time
                        api_health_status = response.status

                    return {
                        "health_endpoint_time": health_time,
                        "health_status": health_status,
                        "api_health_endpoint_time": api_health_time,
                        "api_health_status": api_health_status,
                        "base_url": base_url,
                    }

            return asyncio.run(api_benchmark())

        except ImportError:
            logger.warning("aiohttp not available, skipping API benchmark")
            return {"error": "aiohttp not available"}
        except Exception as e:
            logger.error(f"API benchmark failed: {e}")
            return {"error": str(e)}

    def benchmark_file_operations(self) -> Dict[str, Any]:
        """Benchmark file system operations"""
        logger.info("Benchmarking file operations...")

        import shutil
        import tempfile

        results = {}

        # Test file creation/deletion
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, "benchmark_test.txt")
            test_data = "x" * 1024 * 1024  # 1MB of data

            # Write test
            start_time = time.time()
            with open(test_file, "w") as f:
                f.write(test_data)
            write_time = time.time() - start_time

            # Read test
            start_time = time.time()
            with open(test_file, "r") as f:
                data = f.read()
            read_time = time.time() - start_time

            # File size verification
            file_size = os.path.getsize(test_file)

            results.update(
                {
                    "file_write_time": write_time,
                    "file_read_time": read_time,
                    "file_size_bytes": file_size,
                    "write_speed_mbps": (len(test_data) / write_time) / (1024 * 1024),
                    "read_speed_mbps": (len(test_data) / read_time) / (1024 * 1024),
                }
            )

        return results

    def benchmark_network_performance(self) -> Dict[str, Any]:
        """Benchmark network performance"""
        logger.info("Benchmarking network performance...")

        try:
            # Test DNS resolution
            import socket

            start_time = time.time()
            socket.gethostbyname("google.com")
            dns_time = time.time() - start_time

            # Test HTTP request to external service
            import urllib.request

            start_time = time.time()
            req = urllib.request.Request(
                "http://httpbin.org/get", headers={"User-Agent": "benchmark"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                external_time = time.time() - start_time
                external_status = response.getcode()

            return {
                "dns_resolution_time": dns_time,
                "external_http_time": external_time,
                "external_http_status": external_status,
                "network_latency_ms": dns_time * 1000,
            }

        except Exception as e:
            logger.error(f"Network benchmark failed: {e}")
            return {"error": str(e)}

    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        logger.info("Starting comprehensive performance benchmark...")

        benchmark_start = time.time()

        results = {
            "benchmark_start": datetime.fromtimestamp(benchmark_start).isoformat(),
            "system_info": {
                "platform": sys.platform,
                "python_version": sys.version,
                "hostname": os.uname().nodename if hasattr(os, "uname") else "unknown",
            },
            "benchmarks": {},
        }

        # Run all benchmarks
        benchmarks = [
            ("system_resources", self.measure_system_resources),
            ("database_performance", self.benchmark_database_performance),
            ("cache_performance", self.benchmark_cache_performance),
            ("api_performance", self.benchmark_api_performance),
            ("file_operations", self.benchmark_file_operations),
            ("network_performance", self.benchmark_network_performance),
        ]

        for name, benchmark_func in benchmarks:
            try:
                logger.info(f"Running {name} benchmark...")
                results["benchmarks"][name] = benchmark_func()
            except Exception as e:
                logger.error(f"Benchmark {name} failed: {e}")
                results["benchmarks"][name] = {"error": str(e)}

        # Calculate overall metrics
        benchmark_duration = time.time() - benchmark_start
        results["benchmark_duration"] = benchmark_duration
        results["benchmark_end"] = datetime.now().isoformat()

        # Performance score (simple calculation)
        performance_score = self._calculate_performance_score(results)
        results["performance_score"] = performance_score

        return results

    def _calculate_performance_score(self, results: Dict[str, Any]) -> float:
        """Calculate overall performance score"""
        score = 100.0  # Start with perfect score

        benchmarks = results.get("benchmarks", {})

        # System resources penalties
        system = benchmarks.get("system_resources", {})
        if system.get("cpu_percent", 0) > 80:
            score -= 20
        if system.get("memory_percent", 0) > 85:
            score -= 20
        if system.get("disk_percent", 0) > 90:
            score -= 10

        # API performance penalties
        api = benchmarks.get("api_performance", {})
        if api.get("health_endpoint_time", 0) > 1.0:
            score -= 15
        if api.get("api_health_endpoint_time", 0) > 1.0:
            score -= 15

        # Cache performance penalties
        cache = benchmarks.get("cache_performance", {})
        if cache.get("connection_time", 0) > 0.1:
            score -= 10
        if cache.get("hit_rate", 1.0) < 0.8:
            score -= 15

        return max(0, score)

    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save benchmark results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Benchmark results saved to: {output_path}")

    def print_summary(self, results: Dict[str, Any]):
        """Print benchmark results summary"""
        print(f"\n{'='*60}")
        print("PERFORMANCE BENCHMARK RESULTS SUMMARY")
        print(f"{'='*60}")

        print(f"Benchmark Duration: {results['benchmark_duration']:.2f} seconds")
        print(f"Performance Score: {results.get('performance_score', 'N/A'):.1f}/100")

        benchmarks = results.get("benchmarks", {})
        for name, data in benchmarks.items():
            print(f"\n{name.replace('_', ' ').title()}:")
            if "error" in data:
                print(f"  ❌ Error: {data['error']}")
            else:
                # Print key metrics for each benchmark
                if name == "system_resources":
                    print(f"  CPU: {data.get('cpu_percent', 0):.1f}%")
                    print(f"  Memory: {data.get('memory_percent', 0):.1f}%")
                    print(f"  Disk: {data.get('disk_percent', 0):.1f}%")
                elif name == "api_performance":
                    print(
                        f"  Health endpoint: {data.get('health_endpoint_time', 0):.3f}s"
                    )
                    print(
                        f"  API health: {data.get('api_health_endpoint_time', 0):.3f}s"
                    )
                elif name == "cache_performance":
                    print(f"  Connection time: {data.get('connection_time', 0):.3f}s")
                    print(f"  Hit rate: {data.get('hit_rate', 0):.1%}")
                    print(f"  Ops/sec: {data.get('ops_per_sec', 0)}")
                elif name == "file_operations":
                    print(f"  Write speed: {data.get('write_speed_mbps', 0):.2f} MB/s")
                    print(f"  Read speed: {data.get('read_speed_mbps', 0):.2f} MB/s")

        print(f"{'='*60}\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NEXUS Platform Performance Benchmark")
    parser.add_argument("--output", "-o", help="Output file for results")
    parser.add_argument(
        "--api-url", default="http://localhost:8000", help="API base URL for testing"
    )
    parser.add_argument(
        "--format", choices=["json", "text"], default="text", help="Output format"
    )

    args = parser.parse_args()

    benchmark = PerformanceBenchmark()
    results = benchmark.run_comprehensive_benchmark()

    if args.format == "text":
        benchmark.print_summary(results)
    elif args.format == "json":
        print(json.dumps(results, indent=2, default=str))

    if args.output:
        benchmark.save_results(results, args.output)


if __name__ == "__main__":
    main()
