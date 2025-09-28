# Consolidated file from conftest.py
# Generated on 2025-09-24T15:09:04.061395

# === conftest.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Test Configuration
Pytest configuration and fixtures for comprehensive testing
"""

import asyncio
import sys

import pytest

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from nexus_backend.main import app
from nexus_backend.security.secrets_manager import secrets_manager

# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")

@pytest.fixture(scope="function")

@pytest.fixture(scope="function")

@pytest.fixture(scope="function")

@pytest.fixture(scope="function")

@pytest.fixture(scope="function")

@pytest.fixture(scope="function")

@pytest.fixture(scope="function")

# Test data cleanup
@pytest.fixture(autouse=True)


# === conftest.py ===
"""
Pytest configuration and fixtures for backend tests
"""

import asyncio
import os
# Import the main FastAPI app
import sys
import tempfile

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")

@pytest.fixture

@pytest.fixture

@pytest.fixture

@pytest.fixture

@pytest.fixture

@pytest.fixture

@pytest.fixture
