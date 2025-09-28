#!/usr/bin/env python3
"""
NEXUS Platform - Load Testing Script
Comprehensive load testing for API endpoints
"""

import argparse
import asyncio
import json
import logging
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LoadTester:
    """Load testing for NEXUS Platform API"""

    def __init__(self, base_url: str = "http://localhost:8000", auth_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session: Optional[aiohttp.ClientSession] = None
        self.results: Dict[str, Any] = {}

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=1000, limit_per_host=100)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self._get_headers()
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'NEXUS-LoadTester/1.0'
        }
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'
        return headers

    async def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a single HTTP request"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            if method.upper() == 'GET':
                async with self.session.get(url) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    return {
                        'status': response.status,
                        'response_time': response_time,
                        'content_length': len(content),
                        'success': response.status < 400
                    }
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    response_time = time.time() - start_time
                    content = await response.text()
                    return {
                        'status': response.status,
                        'response_time': response_time,
                        'content_length': len(content),
                        'success': response.status < 400
                    }
            else:
                raise ValueError(f"Unsupported method: {method}")

        except Exception as e:
            response_time = time.time() - start_time
            return {
                'status': 0,
                'response_time': response_time,
                'error': str(e),
                'success': False
            }

    async def run_load_test(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Run load test with given configuration"""
        endpoint = config['endpoint']
        method = config.get('method', 'GET')
        data = config.get('data')
        num_requests = config.get('num_requests', 100)
        concurrent_users = config.get('concurrent_users', 10)
        duration = config.get('duration', 60)  # seconds

        logger.info(f"Starting load test: {method} {endpoint}")
        logger.info(f"Requests: {num_requests}, Concurrent users: {concurrent_users}, Duration: {duration}s")

        results = []
        start_time = time.time()
        request_count = 0

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_users)

        async def worker():
            nonlocal request_count
            while time.time() - start_time < duration and request_count < num_requests:
                async with semaphore:
                    result = await self.make_request(method, endpoint, data)
                    results.append(result)
                    request_count += 1

        # Create worker tasks
        num_workers = min(concurrent_users, num_requests)
        tasks = [asyncio.create_task(worker()) for _ in range(num_workers)]

        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Calculate statistics
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]

        response_times = [r['response_time'] for r in results]
        success_rate = len(successful_requests) / len(results) * 100 if results else 0

        test_results = {
            'endpoint': endpoint,
            'method': method,
            'total_requests': len(results),
            'successful_requests': len(successful_requests),
            'failed_requests': len(failed_requests),
            'success_rate': success_rate,
            'duration': time.time() - start_time,
            'requests_per_second': len(results) / (time.time() - start_time),
            'response_time_stats': {
                'min': min(response_times) if response_times else 0,
                'max': max(response_times) if response_times else 0,
                'avg': statistics.mean(response_times) if response_times else 0,
                'median': statistics.median(response_times) if response_times else 0,
                '95th_percentile': statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times) if response_times else 0,
                '99th_percentile': statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times) if response_times else 0,
            },
            'status_codes': {},
            'errors': []
        }

        # Count status codes
        for result in results:
            status = result.get('status', 0)
            test_results['status_codes'][status] = test_results['status_codes'].get(status, 0) + 1

        # Collect errors
        for result in failed_requests[:10]:  # Limit to first 10 errors
            if 'error' in result:
                test_results['errors'].append(result['error'])

        return test_results

    async def run_scenario_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Run a complex scenario test"""
        name = scenario['name']
        steps = scenario['steps']

        logger.info(f"Running scenario test: {name}")

        scenario_results = {
            'scenario': name,
            'start_time': datetime.now().isoformat(),
            'steps': [],
            'overall_success': True
        }

        for step in steps:
            step_result = await self.run_load_test(step)
            scenario_results['steps'].append(step_result)

            if step_result['success_rate'] < 95:  # Less than 95% success rate
                scenario_results['overall_success'] = False

        scenario_results['end_time'] = datetime.now().isoformat()
        return scenario_results

    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save test results to file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"Results saved to: {output_path}")

    def print_summary(self, results: Dict[str, Any]):
        """Print test results summary"""
        print(f"\n{'='*60}")
        print("LOAD TEST RESULTS SUMMARY"
        print(f"{'='*60}")

        if 'scenario' in results:
            print(f"Scenario: {results['scenario']}")
            print(f"Overall Success: {'✅ PASS' if results['overall_success'] else '❌ FAIL'}")
            print(f"Steps: {len(results['steps'])}")

            for i, step in enumerate(results['steps'], 1):
                print(f"\nStep {i}: {step['method']} {step['endpoint']}")
                print(".1f")
                print(".1f")
                print(".3f")
        else:
            print(f"Endpoint: {results['method']} {results['endpoint']}")
            print(f"Total Requests: {results['total_requests']}")
            print(f"Success Rate: {results['success_rate']:.1f}%")
            print(f"Requests/sec: {results['requests_per_second']:.1f}")
            print(f"Average Response Time: {results['response_time_stats']['avg']:.3f}s")
            print(f"95th Percentile: {results['response_time_stats']['95th_percentile']:.3f}s")
            print(f"99th Percentile: {results['response_time_stats']['99th_percentile']:.3f}s")

        print(f"{'='*60}\n")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NEXUS Platform Load Tester")
    parser.add_argument('--url', default='http://localhost:8000', help='Base URL of the API')
    parser.add_argument('--token', help='Authentication token')
    parser.add_argument('--config', help='Test configuration file')
    parser.add_argument('--output', '-o', help='Output file for results')
    parser.add_argument('--endpoint', help='Single endpoint to test')
    parser.add_argument('--method', default='GET', choices=['GET', 'POST'], help='HTTP method')
    parser.add_argument('--requests', type=int, default=100, help='Number of requests')
    parser.add_argument('--concurrency', type=int, default=10, help='Concurrent users')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')

    args = parser.parse_args()

    async with LoadTester(args.url, args.token) as tester:
        if args.config:
            # Load configuration from file
            with open(args.config, 'r') as f:
                config = json.load(f)

            if 'scenario' in config:
                results = await tester.run_scenario_test(config)
            else:
                results = await tester.run_load_test(config)

        elif args.endpoint:
            # Single endpoint test
            config = {
                'endpoint': args.endpoint,
                'method': args.method,
                'num_requests': args.requests,
                'concurrent_users': args.concurrency,
                'duration': args.duration
            }
            results = await tester.run_load_test(config)
        else:
            parser.error("Either --config or --endpoint must be specified")

        # Print and save results
        tester.print_summary(results)

        if args.output:
            tester.save_results(results, args.output)

        # Exit with appropriate code
        if 'scenario' in results:
            success = results['overall_success']
        else:
            success = results['success_rate'] >= 95

        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
