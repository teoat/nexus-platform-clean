# Consolidated file from test_simple.py
# Generated on 2025-09-24T15:09:04.062033

# === test_simple.py ===
"""
Simple Backend Tests - Direct API Testing
"""

import os
# Import the routes directly
import sys

import pytest

# Create a minimal FastAPI app for testing

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a test app
app = FastAPI(title="NEXUS Platform Test API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and add routes

app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(accounts_router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(transactions_router, prefix="/api/v1/transactions", tags=["transactions"])
app.include_router(analytics_router, prefix="/api/v1/analytics", tags=["analytics"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])

@pytest.fixture

@pytest.fixture

class TestSimpleAPI:
    """Simple API tests."""
    
    
    
    
    
    


# === test_simple.py ===
#!/usr/bin/env python3
"""
NEXUS Platform - Simple Test
Basic test to verify testing infrastructure works
"""

import sys

import pytest

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))




@pytest.mark.unit

@pytest.mark.integration

@pytest.mark.security


