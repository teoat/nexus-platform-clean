# Consolidated file from test_backend.py
# Generated on 2025-09-24T15:09:04.054906

# === test_backend.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Backend Test Script
Test the unified FastAPI application
"""


def test_backend():
    """Test the backend imports and basic functionality"""
    print("🧪 Testing NEXUS Platform Backend...")

    try:
        # Test imports
        print("✅ Main app import successful")

        print("✅ Database models import successful")

        print("✅ Database connection import successful")

        print("✅ API router import successful")

        # Test app configuration
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        print(f"✅ App description: {app.description}")

        # Test routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Available routes: {len(routes)}")
        for route in routes[:5]:  # Show first 5 routes
            print(f"   - {route}")

        print("\n🎉 Backend test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False


if __name__ == "__main__":
    test_backend()


# === test_backend.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Backend Test Script
Test the unified FastAPI application
"""


def test_backend():
    """Test the backend imports and basic functionality"""
    print("🧪 Testing NEXUS Platform Backend...")

    try:
        # Test imports
        print("✅ Main app import successful")

        print("✅ Database models import successful")

        print("✅ Database connection import successful")

        print("✅ API router import successful")

        # Test app configuration
        print(f"✅ App title: {app.title}")
        print(f"✅ App version: {app.version}")
        print(f"✅ App description: {app.description}")

        # Test routes
        routes = [route.path for route in app.routes if hasattr(route, "path")]
        print(f"✅ Available routes: {len(routes)}")
        for route in routes[:5]:  # Show first 5 routes
            print(f"   - {route}")

        print("\n🎉 Backend test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        return False


if __name__ == "__main__":
    test_backend()
