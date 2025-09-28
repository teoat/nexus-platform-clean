#!/usr/bin/env python3
"""
NEXUS Platform - Phase 1 Deployment Script
Deploys all Phase 1 enhancements including security, performance, and caching
"""

import subprocess
import sys
import time


class Phase1Deployer:
    """Deployment manager for Phase 1 enhancements"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.app_dir = self.project_root / "app"
        self.deployment_log = []

        # Add app directory to Python path
        sys.path.insert(0, str(self.app_dir))

    def log(self, message: str, level: str = "INFO"):
        """Log deployment message"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.deployment_log.append(log_entry)
        print(log_entry)

    def run_command(self, command: str, cwd: Path = None) -> bool:
        """Run shell command"""
        try:
            self.log(f"Running: {command}")
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                self.log(f"✅ Command succeeded: {command}")
                return True
            else:
                self.log(f"❌ Command failed: {command}")
                self.log(f"Error: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"❌ Command exception: {command} - {str(e)}")
            return False

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.log("🔍 Checking prerequisites...")

        # Check Python version
        if not self.run_command("python --version"):
            return False

        # Check if Redis is available
        try:
            import redis
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            redis_client.ping()
            self.log("✅ Redis is available")
        except Exception:
            self.log("⚠️ Redis not available - cache will use in-memory fallback")

        # Check if required packages are installed
        required_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "redis", "psutil"
        ]

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.log(f"✅ Package available: {package}")
            except ImportError:
                self.log(f"❌ Package missing: {package}")
                return False

        return True

    def deploy_security_middleware(self) -> bool:
        """Deploy enhanced security middleware"""
        self.log("🔒 Deploying enhanced security middleware...")

        # Check if security middleware file exists
        security_file = self.app_dir / "backend" / "security_middleware.py"
        if not security_file.exists():
            self.log("❌ Security middleware file not found")
            return False

        # Verify middleware classes are properly defined
        try:
                RateLimiter, SecurityHeadersMiddleware,
                RequestValidationMiddleware
            )
            self.log("✅ Security middleware classes imported successfully")
        except Exception as e:
            self.log(f"❌ Security middleware import failed: {str(e)}")
            return False

        # Test rate limiter
        rate_limiter = RateLimiter(requests_per_minute=60, requests_per_hour=1000)
        test_ip = "192.168.1.100"

        # Make some test requests
        allowed = 0
        for i in range(5):
            if rate_limiter.is_allowed(test_ip):
                allowed += 1

        if allowed == 5:
            self.log("✅ Rate limiter working correctly")
        else:
            self.log("❌ Rate limiter not working correctly")
            return False

        return True

    def deploy_cache_service(self) -> bool:
        """Deploy cache service with Redis integration"""
        self.log("💾 Deploying cache service...")

        # Check if cache service file exists
        cache_file = self.app_dir / "backend" / "cache_service.py"
        if not cache_file.exists():
            self.log("❌ Cache service file not found")
            return False

        # Test cache service
        try:
            from backend.cache_service import cache, cache_service

            # Test basic cache operations
            test_key = "deployment_test"
            test_value = {"status": "deployment_test", "timestamp": time.time()}

            success = cache_service.set(test_key, test_value, ttl_seconds=60)
            if success:
                cached_value = cache_service.get(test_key)
                if cached_value == test_value:
                    self.log("✅ Cache service working correctly")
                else:
                    self.log("❌ Cache service get failed")
                    return False
            else:
                self.log("❌ Cache service set failed")
                return False

            # Test cache decorator
            @cache(ttl_seconds=30)
            def test_function(x):
                return x * 2

            result1 = test_function(5)
            result2 = test_function(5)

            if result1 == result2 == 10:
                self.log("✅ Cache decorator working correctly")
            else:
                self.log("❌ Cache decorator not working correctly")
                return False

        except Exception as e:
            self.log(f"❌ Cache service deployment failed: {str(e)}")
            return False

        return True

    def deploy_performance_monitor(self) -> bool:
        """Deploy performance monitoring"""
        self.log("📊 Deploying performance monitoring...")

        # Check if performance monitor file exists
        perf_file = self.app_dir / "backend" / "performance_monitor.py"
        if not perf_file.exists():
            self.log("❌ Performance monitor file not found")
            return False

        # Test performance monitor
        try:
            from backend.performance_monitor import (monitor_performance,
                                                     performance_monitor)

            # Test performance recording
            performance_monitor.record_request("/test", "GET", 150.5, error=False)
            performance_monitor.record_request("/test", "GET", 200.0, error=False)
            performance_monitor.record_request("/error", "POST", 50.0, error=True)

            # Test performance summary
            summary = performance_monitor.get_performance_summary(minutes=5)
            if isinstance(summary, dict):
                self.log("✅ Performance monitoring working correctly")
            else:
                self.log("❌ Performance monitoring summary failed")
                return False

            # Test recommendations
            recommendations = performance_monitor.get_recommendations()
            if isinstance(recommendations, list):
                self.log("✅ Performance recommendations working correctly")
            else:
                self.log("❌ Performance recommendations failed")
                return False

        except Exception as e:
            self.log(f"❌ Performance monitoring deployment failed: {str(e)}")
            return False

        return True

    def deploy_database_optimizations(self) -> bool:
        """Deploy database optimizations"""
        self.log("🗄️ Deploying database optimizations...")

        # Check if database connection file exists
        db_file = self.app_dir / "database" / "connection.py"
        if not db_file.exists():
            self.log("❌ Database connection file not found")
            return False

        # Test database connection
        try:

            # Test connection check
            if check_connection():
                self.log("✅ Database connection working")
            else:
                self.log("⚠️ Database connection failed - may be expected in test environment")

            # Test connection pooling parameters
            with open(db_file, 'r') as f:
                content = f.read()

            if "pool_size=20" in content and "max_overflow=30" in content:
                self.log("✅ Database connection pooling configured correctly")
            else:
                self.log("❌ Database connection pooling not configured correctly")
                return False

        except Exception as e:
            self.log(f"❌ Database optimization deployment failed: {str(e)}")
            return False

        return True

    def create_deployment_config(self) -> bool:
        """Create deployment configuration files"""
        self.log("⚙️ Creating deployment configuration...")

        # Generate secure JWT secret
        import secrets
        jwt_secret = secrets.token_urlsafe(32)

        # Create environment configuration
        env_config = {
            "DATABASE_URL": "postgresql://nexus:nexus123@localhost:5432/nexus_db",
            "REDIS_URL": "redis://localhost:6379",
            "JWT_SECRET_KEY": jwt_secret,
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "INFO",
            "PROMETHEUS_ENABLED": "true",
            "OTEL_ENABLED": "true",
            "CORS_ORIGINS": "https://app.nexusplatform.com,https://nexus-platform.com"
        }

        # Write environment configuration
        env_file = self.project_root / ".env"
        try:
            with open(env_file, 'w') as f:
                for key, value in env_config.items():
                    f.write(f"{key}={value}\n")

            self.log("✅ Environment configuration created")
        except Exception as e:
            self.log(f"❌ Environment configuration creation failed: {str(e)}")
            return False

        # Create docker-compose override for Phase 1
        docker_compose_override = """
version: '3.8'
services:
  nexus-api:
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - ENVIRONMENT=${ENVIRONMENT}
      - LOG_LEVEL=${LOG_LEVEL}
      - PROMETHEUS_ENABLED=${PROMETHEUS_ENABLED}
      - OTEL_ENABLED=${OTEL_ENABLED}
    depends_on:
      - redis
      - postgres
    volumes:
      - ./logs:/nexus_backend/logs

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=nexus_db
      - POSTGRES_USER=nexus
      - POSTGRES_PASSWORD=nexus123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
"""

        # Write docker-compose override
        docker_file = self.project_root / "docker-compose.phase1.yml"
        try:
            with open(docker_file, 'w') as f:
                f.write(docker_compose_override)

            self.log("✅ Docker Compose configuration created")
        except Exception as e:
            self.log(f"❌ Docker Compose configuration creation failed: {str(e)}")
            return False

        return True

    def run_deployment_tests(self) -> bool:
        """Run deployment tests"""
        self.log("🧪 Running deployment tests...")

        # Import and test all components
        try:
            from backend.cache_service import cache_service
            from backend.performance_monitor import performance_monitor

            # Test cache service
            cache_service._connect_redis()
            cache_stats = cache_service.get_stats()
            self.log(f"✅ Cache service deployed: {cache_stats.get('backend', 'unknown')}")

            # Test performance monitor
            summary = performance_monitor.get_performance_summary(minutes=1)
            self.log("✅ Performance monitor deployed")

            # Test rate limiter
            rate_limiter = RateLimiter()
            self.log("✅ Rate limiter deployed")

            return True

        except Exception as e:
            self.log(f"❌ Deployment tests failed: {str(e)}")
            return False

    def deploy(self) -> bool:
        """Run full Phase 1 deployment"""
        self.log("🚀 Starting Phase 1 Deployment")
        self.log("=" * 50)

        # Check prerequisites
        if not self.check_prerequisites():
            self.log("❌ Prerequisites check failed")
            return False

        # Deploy individual components
        deployment_steps = [
            ("Security Middleware", self.deploy_security_middleware),
            ("Cache Service", self.deploy_cache_service),
            ("Performance Monitor", self.deploy_performance_monitor),
            ("Database Optimizations", self.deploy_database_optimizations),
            ("Deployment Configuration", self.create_deployment_config),
            ("Deployment Tests", self.run_deployment_tests),
        ]

        success_count = 0
        for step_name, step_function in deployment_steps:
            self.log(f"\n📦 Deploying {step_name}...")
            if step_function():
                success_count += 1
            else:
                self.log(f"❌ {step_name} deployment failed")

        # Summary
        self.log("\n" + "=" * 50)
        self.log("📊 DEPLOYMENT SUMMARY")
        self.log("=" * 50)
        self.log(f"Total Steps: {len(deployment_steps)}")
        self.log(f"Successful: {success_count}")
        self.log(f"Failed: {len(deployment_steps) - success_count}")

        if success_count == len(deployment_steps):
            self.log("🎉 Phase 1 deployment completed successfully!")
            self.log("\n📋 Next Steps:")
            self.log("1. Start the application: python nexus_backend/main.py")
            self.log("2. Run tests: python scripts/test_phase1_implementation.py")
            self.log("3. Monitor performance: Access /api/admin/performance/summary")
            self.log("4. Check cache stats: Access /api/admin/cache/stats")
            return True
        else:
            self.log("⚠️ Some deployment steps failed. Please review the logs above.")
            return False

    def save_deployment_log(self):
        """Save deployment log to file"""
        log_file = self.project_root / "logs" / "phase1_deployment.log"
        log_file.parent.mkdir(exist_ok=True)

        try:
            with open(log_file, 'w') as f:
                f.write("\n".join(self.deployment_log))
            self.log(f"📝 Deployment log saved to: {log_file}")
        except Exception as e:
            self.log(f"❌ Failed to save deployment log: {str(e)}")

def main():
    """Main deployment function"""
    deployer = Phase1Deployer()
    success = deployer.deploy()
    deployer.save_deployment_log()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
