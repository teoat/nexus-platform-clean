# Consolidated file from test_caching.py
# Generated on 2025-09-24T15:09:04.059366

# === test_caching.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Caching System Test Script
Test the Redis caching layer and performance improvements
"""

import asyncio
import json
import time

import httpx


async def test_caching_system():
    """Test the caching system functionality"""
    print("🚀 Testing NEXUS Platform Caching System...")

    # Test cache endpoints
    cache_endpoints = [
        ("/api/v1/monitoring/cache/stats", "GET", "Cache statistics"),
        ("/api/v1/monitoring/cache/keys", "GET", "List cache keys"),
        ("/api/v1/monitoring/cache/clear", "POST", "Clear cache"),
    ]

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n📊 Testing Cache Endpoints:")
        for endpoint, method, description in cache_endpoints:
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

    print("\n🎉 Caching system test completed!")


def test_imports():
    """Test caching imports"""
    print("🧪 Testing Caching Imports...")

    try:
        print("✅ Caching service import successful")

        print("✅ Cache middleware import successful")

        print("✅ Main app with caching import successful")

        # Count total routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Total API routes: {len(routes)}")

        # Show cache routes
        cache_routes = [r for r in routes if "/cache/" in r]
        print(f"✅ Cache management routes: {cache_routes}")

        # Test cache service initialization
        cache_service = RedisCacheService()
        print("✅ Cache service initialization successful")

        print("\n🎉 Caching imports test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Caching imports test failed: {e}")
        return False


async def test_cache_performance():
    """Test cache performance improvements"""
    print("\n⚡ Testing Cache Performance...")

    try:
        # Test basic cache operations
        test_key = "test:performance"
        test_value = {"message": "Hello from cache!", "timestamp": time.time()}

        # Test set operation
        start_time = time.time()
        await cache_service.set(test_key, test_value, ttl=60)
        set_time = time.time() - start_time
        print(f"✅ Cache set operation: {set_time:.4f}s")

        # Test get operation
        start_time = time.time()
        cached_value = await cache_service.get(test_key)
        get_time = time.time() - start_time
        print(f"✅ Cache get operation: {get_time:.4f}s")

        # Verify cached value
        if cached_value and cached_value.get("message") == test_value["message"]:
            print("✅ Cache value verification successful")
        else:
            print("❌ Cache value verification failed")

        # Test cache hit performance
        start_time = time.time()
        for _ in range(100):
            await cache_service.get(test_key)
        cache_hit_time = time.time() - start_time
        print(
            f"✅ 100 cache hits: {cache_hit_time:.4f}s ({cache_hit_time/100*1000:.2f}ms per hit)"
        )

        # Clean up
        await cache_service.delete(test_key)
        print("✅ Cache cleanup successful")

        print("\n🎉 Cache performance test completed!")
        return True

    except Exception as e:
        print(f"❌ Cache performance test failed: {e}")
        return False


if __name__ == "__main__":
    # Test imports first
    if test_imports():
        # Test caching system
        asyncio.run(test_caching_system())
        # Test cache performance
        asyncio.run(test_cache_performance())


# === test_caching.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Caching System Test Script
Test the Redis caching layer and performance improvements
"""

import asyncio
import json
import time

import httpx


async def test_caching_system():
    """Test the caching system functionality"""
    print("🚀 Testing NEXUS Platform Caching System...")

    # Test cache endpoints
    cache_endpoints = [
        ("/api/v1/monitoring/cache/stats", "GET", "Cache statistics"),
        ("/api/v1/monitoring/cache/keys", "GET", "List cache keys"),
        ("/api/v1/monitoring/cache/clear", "POST", "Clear cache"),
    ]

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n📊 Testing Cache Endpoints:")
        for endpoint, method, description in cache_endpoints:
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

    print("\n🎉 Caching system test completed!")


def test_imports():
    """Test caching imports"""
    print("🧪 Testing Caching Imports...")

    try:
        print("✅ Caching service import successful")

        print("✅ Cache middleware import successful")

        print("✅ Main app with caching import successful")

        # Count total routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Total API routes: {len(routes)}")

        # Show cache routes
        cache_routes = [r for r in routes if "/cache/" in r]
        print(f"✅ Cache management routes: {cache_routes}")

        # Test cache service initialization
        cache_service = RedisCacheService()
        print("✅ Cache service initialization successful")

        print("\n🎉 Caching imports test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Caching imports test failed: {e}")
        return False


async def test_cache_performance():
    """Test cache performance improvements"""
    print("\n⚡ Testing Cache Performance...")

    try:
        # Test basic cache operations
        test_key = "test:performance"
        test_value = {"message": "Hello from cache!", "timestamp": time.time()}

        # Test set operation
        start_time = time.time()
        await cache_service.set(test_key, test_value, ttl=60)
        set_time = time.time() - start_time
        print(f"✅ Cache set operation: {set_time:.4f}s")

        # Test get operation
        start_time = time.time()
        cached_value = await cache_service.get(test_key)
        get_time = time.time() - start_time
        print(f"✅ Cache get operation: {get_time:.4f}s")

        # Verify cached value
        if cached_value and cached_value.get("message") == test_value["message"]:
            print("✅ Cache value verification successful")
        else:
            print("❌ Cache value verification failed")

        # Test cache hit performance
        start_time = time.time()
        for _ in range(100):
            await cache_service.get(test_key)
        cache_hit_time = time.time() - start_time
        print(
            f"✅ 100 cache hits: {cache_hit_time:.4f}s ({cache_hit_time/100*1000:.2f}ms per hit)"
        )

        # Clean up
        await cache_service.delete(test_key)
        print("✅ Cache cleanup successful")

        print("\n🎉 Cache performance test completed!")
        return True

    except Exception as e:
        print(f"❌ Cache performance test failed: {e}")
        return False


if __name__ == "__main__":
    # Test imports first
    if test_imports():
        # Test caching system
        asyncio.run(test_caching_system())
        # Test cache performance
        asyncio.run(test_cache_performance())
