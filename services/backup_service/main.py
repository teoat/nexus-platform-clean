#!/usr/bin/env python3
"""
NEXUS Platform - Backup Service
Automated backup and recovery system for production deployment
"""

import asyncio
import gzip
import hashlib
import json
import logging
import os
import signal
import subprocess
import sys
import tarfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import boto3
import psycopg2
import redis
import uvicorn
from botocore.exceptions import ClientError
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("/app/logs/backup-service.log"),
    ],
)
logger = logging.getLogger(__name__)


class BackupService:
    """Production-ready backup and recovery service"""

    def __init__(self):
        self.config = self.load_config()
        self.backup_dir = Path(self.config.get("backup_directory", "/app/backups"))
        self.backup_dir.mkdir(exist_ok=True)

        # Initialize AWS S3 if configured
        self.s3_client = None
        if self.config.get("aws_s3", {}).get("enabled", False):
            try:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=self.config["aws_s3"]["access_key"],
                    aws_secret_access_key=self.config["aws_s3"]["secret_key"],
                    region_name=self.config["aws_s3"]["region"],
                )
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")

        # Initialize database connections
        self.db_config = self.config.get("database", {})
        self.redis_config = self.config.get("redis", {})

    def load_config(self) -> Dict:
        """Load backup configuration"""
        config_files = [
            "/app/config/backup.json",
            "/app/backup_config.json",
            "backup_config.json",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, "r") as f:
                        return json.load(f)
                except Exception as e:
                    logger.warning(f"Failed to load config from {config_file}: {e}")

        # Default configuration
        return {
            "backup_directory": "/app/backups",
            "retention_days": 30,
            "max_backups": 10,
            "schedule": "0 2 * * *",  # Daily at 2 AM
            "database": {
                "host": os.getenv("POSTGRES_HOST", "postgres"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "database": os.getenv("POSTGRES_DB", "nexus_platform"),
                "user": os.getenv("POSTGRES_USER", "nexus"),
                "password": os.getenv("POSTGRES_PASSWORD", ""),
            },
            "redis": {
                "host": os.getenv("REDIS_HOST", "redis"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "password": os.getenv("REDIS_PASSWORD", ""),
            },
            "aws_s3": {
                "enabled": False,
                "bucket": os.getenv("S3_BUCKET", ""),
                "region": os.getenv("S3_REGION", "us-east-1"),
                "access_key": os.getenv("S3_ACCESS_KEY", ""),
                "secret_key": os.getenv("S3_SECRET_KEY", ""),
            },
            "encryption": {
                "enabled": True,
                "key": os.getenv("BACKUP_ENCRYPTION_KEY", ""),
            },
        }

    async def create_database_backup(self) -> str:
        """Create PostgreSQL database backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"database_backup_{timestamp}.sql.gz"

            # pg_dump command
            cmd = [
                "pg_dump",
                "-h",
                self.db_config["host"],
                "-p",
                str(self.db_config["port"]),
                "-U",
                self.db_config["user"],
                "-d",
                self.db_config["database"],
                "--no-password",
                "--format=custom",
                "--compress=9",
                "--file",
                str(backup_file),
            ]

            # Set password environment
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_config["password"]

            result = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                logger.info(f"Database backup created: {backup_file}")
                return str(backup_file)
            else:
                error_msg = stderr.decode()
                logger.error(f"Database backup failed: {error_msg}")
                raise Exception(f"Database backup failed: {error_msg}")

        except Exception as e:
            logger.error(f"Database backup error: {e}")
            raise

    async def create_redis_backup(self) -> str:
        """Create Redis data backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"redis_backup_{timestamp}.rdb"

            # Use redis-cli to save RDB file
            cmd = [
                "redis-cli",
                "-h",
                self.redis_config["host"],
                "-p",
                str(self.redis_config["port"]),
                "--rdb",
                str(backup_file),
            ]

            if self.redis_config.get("password"):
                cmd.extend(["-a", self.redis_config["password"]])

            result = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                logger.info(f"Redis backup created: {backup_file}")
                return str(backup_file)
            else:
                error_msg = stderr.decode()
                logger.error(f"Redis backup failed: {error_msg}")
                raise Exception(f"Redis backup failed: {error_msg}")

        except Exception as e:
            logger.error(f"Redis backup error: {e}")
            raise

    async def create_file_backup(self, source_dirs: List[str]) -> str:
        """Create file system backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"files_backup_{timestamp}.tar.gz"

            # Create tar.gz archive
            with tarfile.open(backup_file, "w:gz") as tar:
                for source_dir in source_dirs:
                    source_path = Path(source_dir)
                    if source_path.exists():
                        tar.add(str(source_path), arcname=source_path.name)

            logger.info(f"File backup created: {backup_file}")
            return str(backup_file)

        except Exception as e:
            logger.error(f"File backup error: {e}")
            raise

    async def encrypt_backup(self, backup_file: str) -> str:
        """Encrypt backup file using AES-256"""
        if not self.config.get("encryption", {}).get("enabled", False):
            return backup_file

        try:
            encrypted_file = f"{backup_file}.enc"
            key = self.config["encryption"]["key"]

            # Use openssl for encryption
            cmd = [
                "openssl",
                "enc",
                "-aes-256-cbc",
                "-salt",
                "-pbkdf2",
                "-in",
                backup_file,
                "-out",
                encrypted_file,
                "-k",
                key,
            ]

            result = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await result.communicate()

            if result.returncode == 0:
                # Remove original file
                os.remove(backup_file)
                logger.info(f"Backup encrypted: {encrypted_file}")
                return encrypted_file
            else:
                error_msg = stderr.decode()
                logger.error(f"Encryption failed: {error_msg}")
                raise Exception(f"Encryption failed: {error_msg}")

        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise

    async def upload_to_s3(self, backup_file: str) -> bool:
        """Upload backup to AWS S3"""
        if not self.s3_client:
            return False

        try:
            bucket = self.config["aws_s3"]["bucket"]
            key = f"backups/{Path(backup_file).name}"

            self.s3_client.upload_file(backup_file, bucket, key)
            logger.info(f"Backup uploaded to S3: s3://{bucket}/{key}")
            return True

        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            return False

    async def cleanup_old_backups(self):
        """Remove old backups based on retention policy"""
        try:
            retention_days = self.config.get("retention_days", 30)
            max_backups = self.config.get("max_backups", 10)

            # Get all backup files
            backup_files = list(self.backup_dir.glob("*"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Remove files older than retention period
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            for backup_file in backup_files:
                if datetime.fromtimestamp(backup_file.stat().st_mtime) < cutoff_date:
                    backup_file.unlink()
                    logger.info(f"Removed old backup: {backup_file}")

            # Keep only the most recent max_backups files
            if len(backup_files) > max_backups:
                for old_file in backup_files[max_backups:]:
                    if old_file.exists():
                        old_file.unlink()
                        logger.info(f"Removed excess backup: {old_file}")

        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def run_full_backup(self) -> Dict:
        """Run complete backup operation"""
        try:
            logger.info("Starting full backup operation")

            # Create backups
            db_backup = await self.create_database_backup()
            redis_backup = await self.create_redis_backup()
            file_backup = await self.create_file_backup(
                ["/app/config", "/app/data", "/app/logs"]
            )

            # Encrypt backups
            backups = [db_backup, redis_backup, file_backup]
            encrypted_backups = []
            for backup in backups:
                encrypted = await self.encrypt_backup(backup)
                encrypted_backups.append(encrypted)

            # Upload to S3
            s3_uploads = []
            for backup in encrypted_backups:
                success = await self.upload_to_s3(backup)
                s3_uploads.append(success)

            # Cleanup old backups
            await self.cleanup_old_backups()

            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "backups": encrypted_backups,
                "s3_uploads": s3_uploads,
                "message": "Full backup completed successfully",
            }

            logger.info("Full backup operation completed")
            return result

        except Exception as e:
            error_result = {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "message": "Backup operation failed",
            }
            logger.error(f"Backup operation failed: {e}")
            return error_result


# FastAPI Application
app = FastAPI(
    title="NEXUS Backup Service",
    description="Automated backup and recovery system",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

backup_service = BackupService()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "backup-service",
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/backup/full")
async def trigger_full_backup(background_tasks: BackgroundTasks):
    """Trigger full backup operation"""
    try:
        # Run backup in background
        background_tasks.add_task(backup_service.run_full_backup)

        return {
            "status": "accepted",
            "message": "Full backup operation started",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start backup: {str(e)}")


@app.get("/backup/status")
async def get_backup_status():
    """Get backup status and recent backups"""
    try:
        backup_files = list(backup_service.backup_dir.glob("*"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        recent_backups = []
        for backup_file in backup_files[:10]:  # Last 10 backups
            recent_backups.append(
                {
                    "filename": backup_file.name,
                    "size": backup_file.stat().st_size,
                    "created": datetime.fromtimestamp(
                        backup_file.stat().st_mtime
                    ).isoformat(),
                    "path": str(backup_file),
                }
            )

        return {
            "status": "success",
            "backup_directory": str(backup_service.backup_dir),
            "recent_backups": recent_backups,
            "total_backups": len(backup_files),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get backup status: {str(e)}"
        )


@app.post("/backup/cleanup")
async def trigger_cleanup():
    """Trigger cleanup of old backups"""
    try:
        await backup_service.cleanup_old_backups()

        return {
            "status": "success",
            "message": "Backup cleanup completed",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to cleanup backups: {str(e)}"
        )


async def main():
    """Main application entry point"""

    # Setup signal handlers
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the FastAPI server
    logger.info("Starting NEXUS Backup Service...")
    config = uvicorn.Config(app, host="0.0.0.0", port=4100, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
