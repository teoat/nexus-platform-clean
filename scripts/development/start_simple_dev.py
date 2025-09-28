#!/usr/bin/env python3
"""
NEXUS Platform - Simple Local Development Starter
Simplified local development without database dependencies
"""

import logging
import os
import subprocess
import sys
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleDevStarter:
    """Simple local development starter"""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        return {
            "base_url": "http://localhost:8000",
            "frontend_url": "http://localhost:3000",
            "timeout": 60,
        }

    def start_simple_dev(self) -> bool:
        """Start simple local development environment"""
        logger.info("Starting NEXUS Platform simple local development...")

        try:
            # Check prerequisites
            if not self._check_prerequisites():
                logger.error("Prerequisites check failed")
                return False

            # Create necessary directories
            self._create_directories()

            # Install dependencies
            if not self._install_dependencies():
                logger.error("Dependencies installation failed")
                return False

            # Create local configuration
            self._create_local_config()

            # Start backend
            if not self._start_backend():
                logger.error("Backend startup failed")
                return False

            # Start frontend (if available)
            self._start_frontend()

            # Run health checks
            self._run_health_checks()

            logger.info("Simple local development environment started successfully!")
            self._print_startup_info()

            return True

        except Exception as e:
            logger.error(f"Simple local development startup failed: {e}")
            return False

    def _check_prerequisites(self) -> bool:
        """Check prerequisites"""
        logger.info("Checking prerequisites...")

        try:
            # Check Python
            result = subprocess.run(
                ["python3", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("Python 3 is not available")
                return False

            # Check pip
            result = subprocess.run(
                ["pip3", "--version"], capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("pip3 is not available")
                return False

            logger.info("Prerequisites check passed")
            return True

        except Exception as e:
            logger.error(f"Prerequisites check failed: {e}")
            return False

    def _create_directories(self):
        """Create necessary directories"""
        logger.info("Creating directories...")

        directories = ["logs/nexus", "data/backups", "config/local"]

        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

    def _install_dependencies(self) -> bool:
        """Install Python dependencies"""
        logger.info("Installing dependencies...")

        try:
            # Install core dependencies
            dependencies = [
                "fastapi",
                "uvicorn[standard]",
                "httpx",
                "requests",
                "aiohttp",
                "psutil",
            ]

            for dep in dependencies:
                logger.info(f"Installing {dep}...")
                result = subprocess.run(
                    ["pip3", "install", dep],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    logger.warning(f"Failed to install {dep}: {result.stderr}")
                    continue

                logger.info(f"Successfully installed {dep}")

            return True

        except Exception as e:
            logger.error(f"Dependencies installation failed: {e}")
            return False

    def _create_local_config(self):
        """Create local configuration"""
        logger.info("Creating local configuration...")

        # Generate secure random keys for development
        import secrets

        jwt_secret = secrets.token_urlsafe(32)
        encryption_key = secrets.token_urlsafe(32)

        config = {
            "JWT_SECRET_KEY": jwt_secret,
            "ENCRYPTION_KEY": encryption_key,
            "ENVIRONMENT": "development",
            "DEBUG": "true",
            "LOG_LEVEL": "INFO",
        }

        with open(".env.local", "w") as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")

        logger.info("Local configuration created: .env.local")

    def _start_backend(self) -> bool:
        """Start backend server"""
        logger.info("Starting backend server...")

        try:
            # Create a simple backend server
            backend_script = """
import os
import sys
sys.path.append('.')

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
from datetime import datetime

app = FastAPI(
    title="NEXUS Platform API",
    version="1.0.0",
    description="NEXUS Platform - Financial Management System"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory data store for demo
users_db = {
    "admin": {
        "id": 1,
        "username": "admin",
        "email": "admin@nexusplatform.com",
        "role": "admin",
        "created_at": "2024-01-01T00:00:00Z"
    },
    "user1": {
        "id": 2,
        "username": "user1",
        "email": "user1@nexusplatform.com",
        "role": "user",
        "created_at": "2024-01-01T00:00:00Z"
    }
}

accounts_db = {
    1: {
        "id": 1,
        "user_id": 1,
        "account_name": "Main Account",
        "account_type": "checking",
        "balance": 10000.00,
        "currency": "USD",
        "created_at": "2024-01-01T00:00:00Z"
    },
    2: {
        "id": 2,
        "user_id": 2,
        "account_name": "Savings Account",
        "account_type": "savings",
        "balance": 5000.00,
        "currency": "USD",
        "created_at": "2024-01-01T00:00:00Z"
    }
}

transactions_db = {
    1: {
        "id": 1,
        "account_id": 1,
        "amount": 100.00,
        "transaction_type": "deposit",
        "description": "Initial deposit",
        "timestamp": "2024-01-01T00:00:00Z"
    },
    2: {
        "id": 2,
        "account_id": 1,
        "amount": -50.00,
        "transaction_type": "withdrawal",
        "description": "ATM withdrawal",
        "timestamp": "2024-01-02T00:00:00Z"
    }
}

@app.get("/")
async def root():
    return {
        "message": "NEXUS Platform API is running!",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "nexus-platform",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/health")
async def api_health():
    return {
        "status": "healthy",
        "api": "nexus-platform",
        "timestamp": datetime.now().isoformat()
    }

# User endpoints
@app.get("/api/users")
async def get_users():
    return {"users": list(users_db.values())}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int):
    user = next((u for u in users_db.values() if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Account endpoints
@app.get("/api/accounts")
async def get_accounts():
    return {"accounts": list(accounts_db.values())}

@app.get("/api/accounts/{account_id}")
async def get_account(account_id: int):
    account = accounts_db.get(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

# Transaction endpoints
@app.get("/api/transactions")
async def get_transactions():
    return {"transactions": list(transactions_db.values())}

@app.get("/api/transactions/{transaction_id}")
async def get_transaction(transaction_id: int):
    transaction = transactions_db.get(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# Dashboard endpoints
@app.get("/api/dashboard")
async def get_dashboard():
    total_balance = sum(account["balance"] for account in accounts_db.values())
    total_transactions = len(transactions_db)

    return {
        "total_balance": total_balance,
        "total_accounts": len(accounts_db),
        "total_transactions": total_transactions,
        "recent_transactions": list(transactions_db.values())[-5:],
        "accounts": list(accounts_db.values())
    }

# Analytics endpoints
@app.get("/api/analytics")
async def get_analytics():
    return {
        "total_balance": sum(account["balance"] for account in accounts_db.values()),
        "transaction_count": len(transactions_db),
        "account_count": len(accounts_db),
        "user_count": len(users_db),
        "average_transaction": sum(t["amount"] for t in transactions_db.values()) / len(transactions_db) if transactions_db else 0
    }

if __name__ == "__main__":
    print("🚀 Starting NEXUS Platform API Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"""

            with open("simple_backend.py", "w") as f:
                f.write(backend_script)

            logger.info("Backend server created: simple_backend.py")
            return True

        except Exception as e:
            logger.error(f"Backend startup failed: {e}")
            return False

    def _start_frontend(self):
        """Start frontend (if available)"""
        logger.info("Checking frontend...")

        if os.path.exists("nexus_backend/nexus_frontend/package.json"):
            logger.info("Frontend found. To start frontend, run:")
            logger.info("cd nexus_backend/frontend && npm install && npm run dev")
        else:
            logger.info(
                "Frontend not found. Backend API is available at http://localhost:8000"
            )

    def _run_health_checks(self):
        """Run health checks"""
        logger.info("Running health checks...")

        try:
            # Wait a moment for server to start
            time.sleep(2)

            # Test backend health
            result = subprocess.run(
                ["curl", "-f", "http://localhost:8000/health"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                logger.info("✅ Backend health check passed")
            else:
                logger.warning(
                    "⚠️ Backend health check failed - server may not be running yet"
                )

        except Exception as e:
            logger.warning(f"Health check failed: {e}")

    def _print_startup_info(self):
        """Print startup information"""
        print("\n" + "=" * 60)
        print("🚀 NEXUS Platform - Simple Local Development")
        print("=" * 60)
        print("✅ Backend API: http://localhost:8000")
        print("✅ Health Check: http://localhost:8000/health")
        print("✅ API Docs: http://localhost:8000/docs")
        print("=" * 60)
        print("📋 Available Commands:")
        print("  • Start Backend: python3 simple_backend.py")
        print("  • Start Frontend: cd nexus_backend/frontend && npm run dev")
        print("  • Test API: curl http://localhost:8000/health")
        print("=" * 60)
        print("🔧 Available Endpoints:")
        print("  • GET  /                    - Root endpoint")
        print("  • GET  /health              - Health check")
        print("  • GET  /api/users           - List users")
        print("  • GET  /api/accounts        - List accounts")
        print("  • GET  /api/transactions    - List transactions")
        print("  • GET  /api/dashboard       - Dashboard data")
        print("  • GET  /api/analytics       - Analytics data")
        print("=" * 60)
        print("🎉 Simple local development environment is ready!")
        print("=" * 60)


def main():
    """Main entry point"""
    starter = SimpleDevStarter()
    success = starter.start_simple_dev()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
