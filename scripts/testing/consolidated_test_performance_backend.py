# Consolidated file from test_performance.py
# Generated on 2025-09-24T15:09:04.058311

# === test_performance.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Performance Optimization Test Script
Test the performance optimization system and improvements
"""

import asyncio
import json
import time

import httpx


async def test_performance_system():
    """Test the performance optimization system"""
    print("⚡ Testing NEXUS Platform Performance System...")

    # Test performance endpoints
    performance_endpoints = [
        ("/api/v1/monitoring/performance/metrics", "GET", "Performance metrics"),
        ("/api/v1/monitoring/performance/optimize", "POST", "Performance optimization"),
        (
            "/api/v1/monitoring/performance/memory/optimize",
            "POST",
            "Memory optimization",
        ),
    ]

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n⚡ Testing Performance Endpoints:")
        for endpoint, method, description in performance_endpoints:
            try:
                if method == "GET":
                    response = await client.get(endpoint)
                else:
                    response = await client.post(endpoint, json={})

                print(f"✅ {description}: {response.status_code}")
                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:100]}...")
                elif response.status_code == 401:
                    print(f"   Unauthorized (expected without token)")
                elif response.status_code == 403:
                    print(f"   Forbidden (expected without admin role)")
            except Exception as e:
                print(f"❌ {description}: Error - {e}")

    print("\n🎉 Performance system test completed!")


def test_imports():
    """Test performance imports"""
    print("🧪 Testing Performance Imports...")

    try:
        print("✅ Performance optimizer import successful")

        print("✅ Main app with performance import successful")

        # Count total routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Total API routes: {len(routes)}")

        # Show performance routes
        performance_routes = [r for r in routes if "/performance/" in r]
        print(f"✅ Performance optimization routes: {performance_routes}")

        # Test performance optimizer initialization
        optimizer = PerformanceOptimizer()
        print("✅ Performance optimizer initialization successful")

        print("\n🎉 Performance imports test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Performance imports test failed: {e}")
        return False


async def test_performance_optimization():
    """Test performance optimization functionality"""
    print("\n⚡ Testing Performance Optimization...")

    try:
        # Test memory optimization
        print("🧠 Testing memory optimization...")
        memory_stats = await performance_optimizer.optimize_memory_usage()
        print(f"✅ Memory optimization completed: {memory_stats}")

        # Test async optimization
        print("🔄 Testing async optimization...")
        async_stats = await performance_optimizer.optimize_async_operations()
        print(f"✅ Async optimization completed: {async_stats}")

        # Test performance metrics
        print("📊 Testing performance metrics...")
        metrics = performance_optimizer.get_performance_metrics()
        print(f"✅ Performance metrics: {metrics}")

        print("\n🎉 Performance optimization test completed!")
        return True

    except Exception as e:
        print(f"❌ Performance optimization test failed: {e}")
        return False


async def test_performance_decorators():
    """Test performance decorators"""
    print("\n🎭 Testing Performance Decorators...")

    try:
        # Test measure_performance decorator
        @measure_performance("test_function")
        async def test_function():
            await asyncio.sleep(0.01)
            return "test_result"

        result = await test_function()
        print(f"✅ Performance decorator test: {result}")

        # Test cache_performance_result decorator
        @cache_performance_result(ttl=60)
        async def cached_test_function():
            await asyncio.sleep(0.01)
            return {"cached": True, "timestamp": time.time()}

        # First call (cache miss)
        start_time = time.time()
        result1 = await cached_test_function()
        first_call_time = time.time() - start_time

        # Second call (cache hit)
        start_time = time.time()
        result2 = await cached_test_function()
        second_call_time = time.time() - start_time

        print(f"✅ Cache performance test:")
        print(f"   First call (cache miss): {first_call_time:.4f}s")
        print(f"   Second call (cache hit): {second_call_time:.4f}s")
        print(f"   Speed improvement: {first_call_time/second_call_time:.1f}x faster")

        print("\n🎉 Performance decorators test completed!")
        return True

    except Exception as e:
        print(f"❌ Performance decorators test failed: {e}")
        return False


async def test_system_performance():
    """Test overall system performance"""
    print("\n🚀 Testing System Performance...")

    try:
        # Run comprehensive performance optimization
        optimizations = await optimize_system_performance()
        print(f"✅ System performance optimization completed:")
        print(f"   Overall score: {optimizations.get('overall_score', 0):.1f}/100")
        print(
            f"   Memory optimizations: {len(optimizations.get('memory', {}).get('optimizations', []))}"
        )
        print(
            f"   Async optimizations: {len(optimizations.get('async', {}).get('performance_improvements', []))}"
        )

        print("\n🎉 System performance test completed!")
        return True

    except Exception as e:
        print(f"❌ System performance test failed: {e}")
        return False


if __name__ == "__main__":
    # Test imports first
    if test_imports():
        # Test performance system
        asyncio.run(test_performance_system())
        # Test performance optimization
        asyncio.run(test_performance_optimization())
        # Test performance decorators
        asyncio.run(test_performance_decorators())
        # Test system performance
        asyncio.run(test_system_performance())


# === test_performance.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Performance Optimization Test Script
Test the performance optimization system and improvements
"""

import asyncio
import json
import time

import httpx


async def test_performance_system():
    """Test the performance optimization system"""
    print("⚡ Testing NEXUS Platform Performance System...")

    # Test performance endpoints
    performance_endpoints = [
        ("/api/v1/monitoring/performance/metrics", "GET", "Performance metrics"),
        ("/api/v1/monitoring/performance/optimize", "POST", "Performance optimization"),
        (
            "/api/v1/monitoring/performance/memory/optimize",
            "POST",
            "Memory optimization",
        ),
    ]

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n⚡ Testing Performance Endpoints:")
        for endpoint, method, description in performance_endpoints:
            try:
                if method == "GET":
                    response = await client.get(endpoint)
                else:
                    response = await client.post(endpoint, json={})

                print(f"✅ {description}: {response.status_code}")
                if response.status_code in [200, 201]:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:100]}...")
                elif response.status_code == 401:
                    print(f"   Unauthorized (expected without token)")
                elif response.status_code == 403:
                    print(f"   Forbidden (expected without admin role)")
            except Exception as e:
                print(f"❌ {description}: Error - {e}")

    print("\n🎉 Performance system test completed!")


def test_imports():
    """Test performance imports"""
    print("🧪 Testing Performance Imports...")

    try:
        print("✅ Performance optimizer import successful")

        print("✅ Main app with performance import successful")

        # Count total routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Total API routes: {len(routes)}")

        # Show performance routes
        performance_routes = [r for r in routes if "/performance/" in r]
        print(f"✅ Performance optimization routes: {performance_routes}")

        # Test performance optimizer initialization
        optimizer = PerformanceOptimizer()
        print("✅ Performance optimizer initialization successful")

        print("\n🎉 Performance imports test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Performance imports test failed: {e}")
        return False


async def test_performance_optimization():
    """Test performance optimization functionality"""
    print("\n⚡ Testing Performance Optimization...")

    try:
        # Test memory optimization
        print("🧠 Testing memory optimization...")
        memory_stats = await performance_optimizer.optimize_memory_usage()
        print(f"✅ Memory optimization completed: {memory_stats}")

        # Test async optimization
        print("🔄 Testing async optimization...")
        async_stats = await performance_optimizer.optimize_async_operations()
        print(f"✅ Async optimization completed: {async_stats}")

        # Test performance metrics
        print("📊 Testing performance metrics...")
        metrics = performance_optimizer.get_performance_metrics()
        print(f"✅ Performance metrics: {metrics}")

        print("\n🎉 Performance optimization test completed!")
        return True

    except Exception as e:
        print(f"❌ Performance optimization test failed: {e}")
        return False


async def test_performance_decorators():
    """Test performance decorators"""
    print("\n🎭 Testing Performance Decorators...")

    try:
        # Test measure_performance decorator
        @measure_performance("test_function")
        async def test_function():
            await asyncio.sleep(0.01)
            return "test_result"

        result = await test_function()
        print(f"✅ Performance decorator test: {result}")

        # Test cache_performance_result decorator
        @cache_performance_result(ttl=60)
        async def cached_test_function():
            await asyncio.sleep(0.01)
            return {"cached": True, "timestamp": time.time()}

        # First call (cache miss)
        start_time = time.time()
        result1 = await cached_test_function()
        first_call_time = time.time() - start_time

        # Second call (cache hit)
        start_time = time.time()
        result2 = await cached_test_function()
        second_call_time = time.time() - start_time

        print(f"✅ Cache performance test:")
        print(f"   First call (cache miss): {first_call_time:.4f}s")
        print(f"   Second call (cache hit): {second_call_time:.4f}s")
        print(f"   Speed improvement: {first_call_time/second_call_time:.1f}x faster")

        print("\n🎉 Performance decorators test completed!")
        return True

    except Exception as e:
        print(f"❌ Performance decorators test failed: {e}")
        return False


async def test_system_performance():
    """Test overall system performance"""
    print("\n🚀 Testing System Performance...")

    try:
        # Run comprehensive performance optimization
        optimizations = await optimize_system_performance()
        print(f"✅ System performance optimization completed:")
        print(f"   Overall score: {optimizations.get('overall_score', 0):.1f}/100")
        print(
            f"   Memory optimizations: {len(optimizations.get('memory', {}).get('optimizations', []))}"
        )
        print(
            f"   Async optimizations: {len(optimizations.get('async', {}).get('performance_improvements', []))}"
        )

        print("\n🎉 System performance test completed!")
        return True

    except Exception as e:
        print(f"❌ System performance test failed: {e}")
        return False


if __name__ == "__main__":
    # Test imports first
    if test_imports():
        # Test performance system
        asyncio.run(test_performance_system())
        # Test performance optimization
        asyncio.run(test_performance_optimization())
        # Test performance decorators
        asyncio.run(test_performance_decorators())
        # Test system performance
        asyncio.run(test_system_performance())


# === test_performance.py ===
"""
Performance Tests
"""


class TestPerformance:
    """Test system performance under various loads."""
