# Nexus Platform System Tests

## Overview

This directory contains comprehensive system tests for the Nexus Platform Financial Examiner POV system. The tests cover all major components including the financial examiner system, frontend themes, SSOT integration, and configuration management.

## Test Files

### Core Test Files

- **`test_system.py`** - Main test suite with comprehensive test cases
- **`run_tests.py`** - Simplified test runner with enhanced output
- **`test_config.py`** - Test configuration and mock data
- **`TEST_DOCUMENTATION.md`** - This documentation file

## Test Categories

### 1. Financial Examiner System Tests (`TestFinancialExaminerSystem`)

Tests the core financial examiner functionality:

- **POV Switching** - Tests switching between different points of view (prosecutor, judge, executive, etc.)
- **Financial Data Processing** - Tests reconciliation and analysis of financial data
- **Fraud Detection** - Tests fraud detection algorithms and risk scoring
- **Litigation Management** - Tests case creation, evidence management, and case tracking
- **Report Generation** - Tests various report types and generation

### 2. Frontend Themes Tests (`TestFrontendThemes`)

Tests the frontend theme system:

- **Theme Creation** - Tests creation and configuration of all theme types
- **POV Adaptations** - Tests POV-specific theme adaptations
- **CSS Generation** - Tests CSS generation for all themes

### 3. SSOT Integration Tests (`TestSSOTIntegration`)

Tests integration with the existing SSOT system:

- **SSOT Synchronization** - Tests data synchronization with SSOT
- **Status Retrieval** - Tests SSOT status monitoring
- **Automation Triggering** - Tests SSOT automation triggers
- **Health Monitoring** - Tests system health monitoring

### 4. Configuration Tests (`TestConfiguration`)

Tests configuration management:

- **Config Loading** - Tests configuration file loading
- **Get/Set Operations** - Tests configuration value operations
- **Database URL Generation** - Tests database connection string generation
- **Redis URL Generation** - Tests Redis connection string generation

## Running Tests

### Quick Test Run

```bash
# Run all tests with enhanced output
python NEXUS_nexus_backend/run_tests.py

# Or run tests directly
python NEXUS_nexus_backend/test_system.py
```

### Individual Test Categories

```bash
# Run only financial examiner tests
python -m unittest NEXUS_app.test_system.TestFinancialExaminerSystem

# Run only frontend theme tests
python -m unittest NEXUS_app.test_system.TestFrontendThemes

# Run only SSOT integration tests
python -m unittest NEXUS_app.test_system.TestSSOTIntegration

# Run only configuration tests
python -m unittest NEXUS_app.test_system.TestConfiguration
```

## Test Configuration

The test configuration is managed in `test_config.py` and includes:

- **Test Database** - SQLite database for testing (separate from production)
- **Test Redis** - Redis instance on different DB for testing
- **Mock Data** - Sample financial and litigation data for testing
- **Test Paths** - Dedicated directories for test data and output

## Mock Data

The test suite includes comprehensive mock data:

### Financial Data

- Sample expenses with categories and vendors
- Bank statements with transaction types
- Revenue records with client information

### Litigation Data

- Sample legal cases with parties and issues
- Evidence records with file paths and types
- Case status and timeline information

## Test Environment Setup

### Prerequisites

1. **Python Environment** - Ensure you're using the nexus_env environment
2. **Dependencies** - All required packages should be installed
3. **Test Database** - SQLite will be created automatically
4. **Redis** - Optional, tests will work without Redis

### Environment Variables

```bash
# Optional: Set test-specific environment variables
export NEXUS_TEST_MODE=true
export NEXUS_TEST_DB_PATH=/path/to/test/db
export NEXUS_TEST_REDIS_URL=redis://localhost:6379/15
```

## Test Output

### Success Output

```
🧪 Running Nexus Platform System Tests...
✅ All tests passed!
```

### Failure Output

```
🧪 Running Nexus Platform System Tests...
❌ Some tests failed!
```

### Detailed Output

The test runner provides detailed output including:

- Test case names and status
- Assertion failures with details
- Error messages and stack traces
- Test execution timing

## Continuous Integration

These tests are designed to be run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run System Tests
  run: |
    cd NEXUS_app
    python test_system.py
```

## Troubleshooting

### Common Issues

1. **Import Errors** - Ensure all dependencies are installed
2. **Database Errors** - Check SQLite permissions and paths
3. **Redis Errors** - Ensure Redis is running or tests will use mock data
4. **Path Errors** - Verify workspace path is correct

### Debug Mode

Run tests with debug output:

```bash
# Enable debug logging
export NEXUS_LOG_LEVEL=DEBUG
python NEXUS_nexus_backend/test_system.py
```

## Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ All public methods and functions
- ✅ Error handling and edge cases
- ✅ Data validation and type checking
- ✅ Integration between components
- ✅ Configuration management
- ✅ Async operations and concurrency

## Contributing

When adding new features:

1. **Add Tests** - Create corresponding test cases
2. **Update Mock Data** - Add relevant test data
3. **Document Changes** - Update this documentation
4. **Run Tests** - Ensure all tests pass

## Performance Testing

For performance testing, consider:

- Large dataset processing
- Concurrent user simulation
- Memory usage monitoring
- Response time measurement

## Security Testing

The test suite includes basic security tests:

- Input validation
- SQL injection prevention
- XSS protection
- Authentication and authorization

For comprehensive security testing, use dedicated security testing tools.
