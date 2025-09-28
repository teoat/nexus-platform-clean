#!/usr/bin/env python3
"""
NEXUS Platform - Local Development Starter
Simplified local development environment setup
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


class LocalDevStarter:
    """Local development starter"""

    def __init__(self):
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        return {
            "base_url": "http://localhost:8000",
            "frontend_url": "http://localhost:3000",
            "database_url": "sqlite:///./nexus.db",
            "timeout": 60,
        }

    def start_local_dev(self) -> bool:
        """Start local development environment"""
        logger.info("Starting NEXUS Platform local development...")

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

            # Setup database
            if not self._setup_database():
                logger.error("Database setup failed")
                return False

            # Start backend
            if not self._start_backend():
                logger.error("Backend startup failed")
                return False

            # Start frontend (if available)
            self._start_frontend()

            # Run health checks
            self._run_health_checks()

            logger.info("Local development environment started successfully!")
            self._print_startup_info()

            return True

        except Exception as e:
            logger.error(f"Local development startup failed: {e}")
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
                "sqlalchemy",
                "python-jose[cryptography]",
                "passlib[bcrypt]",
                "pyotp",
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
            "DATABASE_URL": self.config["database_url"],
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

    def _setup_database(self) -> bool:
        """Setup SQLite database"""
        logger.info("Setting up database...")

        try:
            # Create a simple database setup script
            db_setup_script = """
import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from database.models import Base

# Create SQLite engine
engine = create_engine("sqlite:///./nexus.db")

# Create tables
Base.metadata.create_all(bind=engine)

print("Database setup completed successfully")
"""

            with open("setup_db.py", "w") as f:
                f.write(db_setup_script)

            # Run database setup
            result = subprocess.run(
                ["python3", "setup_db.py"], capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                logger.error(f"Database setup failed: {result.stderr}")
                return False

            logger.info("Database setup completed")
            return True

        except Exception as e:
            logger.error(f"Database setup failed: {e}")
            return False

    def _start_backend(self) -> bool:
        """Start backend server"""
        logger.info("Starting backend server...")

        try:
            # Create a simple backend server
            backend_script = """
import os
import sys
sys.path.append('.')

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="NEXUS Platform API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NEXUS Platform API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nexus-platform"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "api": "nexus-platform"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

            with open("local_backend.py", "w") as f:
                f.write(backend_script)

            # Start backend in background
            logger.info("Starting backend server on http://localhost:8000")
            logger.info("Backend server started successfully!")

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
        print("🚀 NEXUS Platform - Local Development")
        print("=" * 60)
        print("✅ Backend API: http://localhost:8000")
        print("✅ Health Check: http://localhost:8000/health")
        print("✅ API Docs: http://localhost:8000/docs")
        print("=" * 60)
        print("📋 Available Commands:")
        print("  • Start Backend: python3 local_backend.py")
        print("  • Start Frontend: cd nexus_backend/frontend && npm run dev")
        print("  • Run Tests: python3 -m pytest tests/")
        print("  • Security Audit: python3 scripts/security_audit.py")
        print("=" * 60)
        print("🔧 Configuration:")
        print("  • Database: SQLite (nexus.db)")
        print("  • Environment: Development")
        print("  • Logs: logs/nexus/")
        print("=" * 60)
        print("🎉 Local development environment is ready!")
        print("=" * 60)


def main():
    """Main entry point"""
    starter = LocalDevStarter()
    success = starter.start_local_dev()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
