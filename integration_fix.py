#!/usr/bin/env python3
"""
NEXUS Platform - Frontend-Backend Integration Fix
Comprehensive solution to fix all integration issues
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests


class NexusIntegrationFixer:
    """Fix all frontend-backend integration issues"""

    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.frontend_path = self.base_path / "frontend" / "web"
        self.backend_path = self.base_path / "backend"

    def fix_all_integration_issues(self):
        """Fix all integration issues"""
        print("🔧 Starting NEXUS Integration Fix...")

        # 1. Fix frontend structure
        self.fix_frontend_structure()

        # 2. Fix backend configuration
        self.fix_backend_configuration()

        # 3. Create proper API configuration
        self.create_api_configuration()

        # 4. Test integration
        self.test_integration()

        print("✅ Integration fix completed!")

    def fix_frontend_structure(self):
        """Fix frontend directory structure"""
        print("📁 Fixing frontend structure...")

        # Ensure src directory exists
        src_dir = self.frontend_path / "src"
        src_dir.mkdir(exist_ok=True)

        # Copy essential files to src
        essential_files = ["index.js", "App.tsx", "index.css"]

        for file in essential_files:
            src_file = self.frontend_path / file
            dest_file = src_dir / file
            if src_file.exists() and not dest_file.exists():
                dest_file.write_text(src_file.read_text())
                print(f"  ✅ Copied {file} to src/")

        # Copy directories to src
        dirs_to_copy = [
            "components",
            "pages",
            "hooks",
            "services",
            "store",
            "config",
            "contexts",
            "providers",
            "types",
            "utils",
        ]

        for dir_name in dirs_to_copy:
            src_dir_path = self.frontend_path / dir_name
            dest_dir_path = src_dir / dir_name
            if src_dir_path.exists() and not dest_dir_path.exists():
                subprocess.run(["cp", "-r", str(src_dir_path), str(dest_dir_path)])
                print(f"  ✅ Copied {dir_name}/ to src/")

    def fix_backend_configuration(self):
        """Fix backend configuration"""
        print("⚙️ Fixing backend configuration...")

        # Create working backend
        backend_working = self.backend_path / "main_working.py"
        if not backend_working.exists():
            print("  ❌ Working backend not found")
            return

        # Update package.json proxy
        package_json = self.frontend_path / "package.json"
        if package_json.exists():
            content = package_json.read_text()
            content = content.replace(
                '"proxy": "http://localhost:8000"', '"proxy": "http://localhost:8001"'
            )
            package_json.write_text(content)
            print("  ✅ Updated proxy configuration")

    def create_api_configuration(self):
        """Create proper API configuration"""
        print("🔗 Creating API configuration...")

        # Create API configuration file
        api_config = self.frontend_path / "src" / "config" / "api.ts"
        api_config.parent.mkdir(parents=True, exist_ok=True)

        api_config_content = """
export const API_CONFIG = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8001',
  ENDPOINTS: {
    HEALTH: '/health',
    API_HEALTH: '/api/health',
    AUTH: {
      REGISTER: '/api/auth/register',
      LOGIN: '/api/auth/login',
      LOGOUT: '/api/auth/logout'
    },
    DASHBOARD: '/api/dashboard',
    ACCOUNTS: '/api/accounts',
    TRANSACTIONS: '/api/transactions',
    ANALYTICS: '/api/analytics'
  }
};

export const apiRequest = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_CONFIG.BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json();
};
"""

        api_config.write_text(api_config_content)
        print("  ✅ Created API configuration")

    def test_integration(self):
        """Test the integration"""
        print("🧪 Testing integration...")

        # Test backend
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ Backend is responding")
            else:
                print(f"  ❌ Backend returned status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Backend not responding: {e}")

        # Test frontend
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print("  ✅ Frontend is responding")
            else:
                print(f"  ❌ Frontend returned status {response.status_code}")
        except Exception as e:
            print(f"  ❌ Frontend not responding: {e}")

        # Test API proxy
        try:
            response = requests.get("http://localhost:3000/api/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ API proxy is working")
            else:
                print(f"  ❌ API proxy returned status {response.status_code}")
        except Exception as e:
            print(f"  ❌ API proxy not working: {e}")


if __name__ == "__main__":
    fixer = NexusIntegrationFixer()
    fixer.fix_all_integration_issues()
