# Consolidated file from run.py
# Generated on 2025-09-24T15:09:04.037340

# === run.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Backend Startup Script
Run the unified FastAPI application
"""

import os
import sys

import uvicorn

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault(
        "DATABASE_URL", "postgresql://nexus:nexus123@localhost:5432/nexus_platform"
    )
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

    # Run the application
    uvicorn.run(
        "nexus_backend.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        access_log=True,
    )


# === run.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Backend Startup Script
Run the unified FastAPI application
"""

import os
import sys

import uvicorn

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault(
        "DATABASE_URL", "postgresql://nexus:nexus123@localhost:5432/nexus_platform"
    )
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

    # Run the application
    uvicorn.run(
        "nexus_backend.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info",
        access_log=True,
    )
