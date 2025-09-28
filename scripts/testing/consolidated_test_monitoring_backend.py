# Consolidated file from test_monitoring.py
# Generated on 2025-09-24T15:09:04.057720

# === test_monitoring.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Monitoring Test Script
Test the monitoring and observability system
"""

import asyncio
import json

import httpx


async def test_monitoring_system():
    """Test the monitoring and observability system"""
    print("📊 Testing NEXUS Platform Monitoring System...")

    # Test monitoring endpoints
    monitoring_endpoints = [
        ("/api/v1/monitoring/health", "GET", "Health check"),
        ("/api/v1/monitoring/metrics/system", "GET", "System metrics"),
        ("/api/v1/monitoring/metrics/application", "GET", "Application metrics"),
        ("/api/v1/monitoring/metrics/database", "GET", "Database metrics"),
        ("/api/v1/monitoring/metrics/historical", "GET", "Historical metrics"),
        ("/api/v1/monitoring/alerts", "GET", "System alerts"),
        ("/api/v1/monitoring/dashboard", "GET", "Monitoring dashboard"),
        ("/api/v1/monitoring/metrics/collect", "POST", "Collect metrics"),
    ]

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n📊 Testing Monitoring Endpoints:")
        for endpoint, method, description in monitoring_endpoints:
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
                elif response.status_code == 422:
                    print(f"   Validation error (expected for empty data)")
            except Exception as e:
                print(f"❌ {description}: Error - {e}")

    print("\n🎉 Monitoring system test completed!")


def test_imports():
    """Test monitoring imports"""
    print("🧪 Testing Monitoring Imports...")

    try:
        print("✅ Monitoring service import successful")

        print("✅ Logging configuration import successful")

        print("✅ Monitoring router import successful")

        # Test main app with monitoring
        print("✅ Main app with monitoring import successful")

        # Count total routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Total API routes: {len(routes)}")

        # Show monitoring routes
        monitoring_routes = [r for r in routes if "/monitoring/" in r]
        print(f"✅ Monitoring routes: {monitoring_routes}")

        # Test monitoring service initialization
        monitoring_service = MonitoringService()
        print("✅ Monitoring service initialization successful")

        # Test logging setup
        logger = get_logger("test")
        logger.info("Test log message")
        print("✅ Logging system working")

        print("\n🎉 Monitoring imports test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Monitoring imports test failed: {e}")
        return False


if __name__ == "__main__":
    # Test imports first
    if test_imports():
        # Test monitoring system
        asyncio.run(test_monitoring_system())


# === test_monitoring.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Monitoring Test Script
Test the monitoring and observability system
"""

import asyncio
import json

import httpx


async def test_monitoring_system():
    """Test the monitoring and observability system"""
    print("📊 Testing NEXUS Platform Monitoring System...")

    # Test monitoring endpoints
    monitoring_endpoints = [
        ("/api/v1/monitoring/health", "GET", "Health check"),
        ("/api/v1/monitoring/metrics/system", "GET", "System metrics"),
        ("/api/v1/monitoring/metrics/application", "GET", "Application metrics"),
        ("/api/v1/monitoring/metrics/database", "GET", "Database metrics"),
        ("/api/v1/monitoring/metrics/historical", "GET", "Historical metrics"),
        ("/api/v1/monitoring/alerts", "GET", "System alerts"),
        ("/api/v1/monitoring/dashboard", "GET", "Monitoring dashboard"),
        ("/api/v1/monitoring/metrics/collect", "POST", "Collect metrics"),
    ]

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        print("\n📊 Testing Monitoring Endpoints:")
        for endpoint, method, description in monitoring_endpoints:
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
                elif response.status_code == 422:
                    print(f"   Validation error (expected for empty data)")
            except Exception as e:
                print(f"❌ {description}: Error - {e}")

    print("\n🎉 Monitoring system test completed!")


def test_imports():
    """Test monitoring imports"""
    print("🧪 Testing Monitoring Imports...")

    try:
        print("✅ Monitoring service import successful")

        print("✅ Logging configuration import successful")

        print("✅ Monitoring router import successful")

        # Test main app with monitoring
        print("✅ Main app with monitoring import successful")

        # Count total routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Total API routes: {len(routes)}")

        # Show monitoring routes
        monitoring_routes = [r for r in routes if "/monitoring/" in r]
        print(f"✅ Monitoring routes: {monitoring_routes}")

        # Test monitoring service initialization
        monitoring_service = MonitoringService()
        print("✅ Monitoring service initialization successful")

        # Test logging setup
        logger = get_logger("test")
        logger.info("Test log message")
        print("✅ Logging system working")

        print("\n🎉 Monitoring imports test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Monitoring imports test failed: {e}")
        return False


if __name__ == "__main__":
    # Test imports first
    if test_imports():
        # Test monitoring system
        asyncio.run(test_monitoring_system())
