**Status**: 🔒 **LOCKED** - SSOT Document
**Version**: 1.0
**Last Updated**: 2025-01-17
**Source**: Consolidated from original documentation

---

# API Reference - Nexus Platform Financial Examiner System

## Overview

This document provides comprehensive API documentation for the Nexus Platform Financial Examiner POV System.

## Core Components

### 1. Financial Examiner System (`financial_examiner_system.py`)

#### POVRole Enum

```python
class POVRole(Enum):
    FINANCIAL_EXAMINER = "financial_examiner"
    PROSECUTOR = "prosecutor"
    JUDGE = "judge"
    EXECUTIVE = "executive"
    COMPLIANCE_OFFICER = "compliance_officer"
    AUDITOR = "auditor"
```

#### UIMode Enum

```python
class UIMode(Enum):
    ECO = "eco"
    USER_GUIDED = "user_guided"
    FULL_AI = "full_ai"
```

#### FinancialExaminerSystem Class

##### Methods

**`__init__(workspace_path: str)`**

- Initialize the Financial Examiner System
- Parameters:
  - `workspace_path`: Path to the workspace directory

**`async switch_pov(pov_role: POVRole) -> bool`**

- Switch to a different POV role
- Parameters:
  - `pov_role`: The POV role to switch to
- Returns: `True` if successful, `False` otherwise

**`async set_ui_mode(ui_mode: UIMode) -> bool`**

- Set the UI mode
- Parameters:
  - `ui_mode`: The UI mode to set
- Returns: `True` if successful, `False` otherwise

**`async process_financial_data(data: Dict[str, Any]) -> Dict[str, Any]`**

- Process financial data through the current POV
- Parameters:
  - `data`: Dictionary containing financial data (expenses, bank_statements)
- Returns: Dictionary with processing results including reconciliation, fraud analysis, and POV-specific analysis

#### ReconciliationEngine Class

**`async process(data: Dict[str, Any]) -> Dict[str, Any]`**

- Process financial reconciliation
- Parameters:
  - `data`: Dictionary containing expenses and bank_statements
- Returns: Dictionary with reconciliation results including matched transactions, unmatched items, and reconciliation rate

#### FraudDetectionSystem Class

**`async analyze(data: Dict[str, Any]) -> Dict[str, Any]`**

- Analyze data for fraud patterns
- Parameters:
  - `data`: Dictionary containing financial data
- Returns: Dictionary with fraud analysis including flags, risk score, and risk level

#### LitigationManagementSystem Class

**`async create_case(case_data: Dict[str, Any]) -> Dict[str, Any]`**

- Create a new litigation case
- Parameters:
  - `case_data`: Dictionary containing case information
- Returns: Dictionary with case details including case_id, status, and creation timestamp

**`async add_evidence(case_id: str, evidence: Dict[str, Any]) -> bool`**

- Add evidence to a case
- Parameters:
  - `case_id`: ID of the case
  - `evidence`: Dictionary containing evidence information
- Returns: `True` if successful, `False` otherwise

#### ReportGenerationSystem Class

**`async generate_report(data: Dict[str, Any], report_type: str) -> Dict[str, Any]`**

- Generate a financial report
- Parameters:
  - `data`: Dictionary containing data for the report
  - `report_type`: Type of report to generate
- Returns: Dictionary with report details including report_id, type, and summary

### 2. Frontend Theme Manager (`frontend_themes.py`)

#### ThemeType Enum

```python
class ThemeType(Enum):
    FINANCIAL_PROFESSIONAL = "financial_professional"
    MODERN_FINANCIAL = "modern_financial"
    EXECUTIVE_DASHBOARD = "executive_dashboard"
    COMPLIANCE_AUDIT = "compliance_audit"
```

#### FrontendThemeManager Class

##### Methods

**`__init__(workspace_path: str)`**

- Initialize the Frontend Theme Manager
- Parameters:
  - `workspace_path`: Path to the workspace directory

**`set_theme(theme: ThemeType) -> bool`**

- Set the current theme
- Parameters:
  - `theme`: The theme to set
- Returns: `True` if successful, `False` otherwise

**`get_current_theme() -> Dict[str, Any]`**

- Get the current theme configuration
- Returns: Dictionary with current theme configuration

**`save_theme_config(theme: ThemeType, pov_role: Optional[str] = None) -> bool`**

- Save theme configuration to file
- Parameters:
  - `theme`: The theme to save
  - `pov_role`: Optional POV role for POV-specific configuration
- Returns: `True` if successful, `False` otherwise

**`save_css(theme: ThemeType, pov_role: Optional[str] = None) -> bool`**

- Generate and save CSS for the theme
- Parameters:
  - `theme`: The theme to generate CSS for
  - `pov_role`: Optional POV role for POV-specific CSS
- Returns: `True` if successful, `False` otherwise

**`get_available_themes() -> List[Dict[str, Any]]`**

- Get list of available themes
- Returns: List of dictionaries with theme information

**`get_theme_preview(theme: ThemeType) -> Dict[str, Any]`**

- Get theme preview information
- Parameters:
  - `theme`: The theme to get preview for
- Returns: Dictionary with theme preview information

### 3. SSOT Integration (`ssot_integration.py`)

#### SSOTIntegration Class

##### Methods

**`__init__(workspace_path: str = "/Users/Arief/Desktop/Nexus")`**

- Initialize SSOT integration
- Parameters:
  - `workspace_path`: Path to the workspace directory

**`async sync_with_ssot() -> bool`**

- Sync Financial Examiner system with SSOT
- Returns: `True` if successful, `False` otherwise

**`async get_ssot_status() -> Dict[str, Any]`**

- Get current SSOT status
- Returns: Dictionary with SSOT status information

**`async trigger_ssot_automation(action: str, data: Dict[str, Any] = None) -> bool`**

- Trigger SSOT automation
- Parameters:
  - `action`: The action to trigger
  - `data`: Optional data for the action
- Returns: `True` if successful, `False` otherwise

**`async monitor_ssot_health() -> Dict[str, Any]`**

- Monitor SSOT system health
- Returns: Dictionary with health status information

### 4. Configuration System (`config.py`)

#### NexusConfig Class

##### Methods

**`__init__(workspace_path: str = "/Users/Arief/Desktop/Nexus")`**

- Initialize configuration system
- Parameters:
  - `workspace_path`: Path to the workspace directory

**`get(key: str, default: Any = None) -> Any`**

- Get configuration value by key
- Parameters:
  - `key`: Configuration key (supports dot notation)
  - `default`: Default value if key not found
- Returns: Configuration value

**`set(key: str, value: Any) -> None`**

- Set configuration value by key
- Parameters:
  - `key`: Configuration key (supports dot notation)
  - `value`: Value to set

**`get_database_url() -> str`**

- Get database connection URL
- Returns: PostgreSQL connection URL

**`get_redis_url() -> str`**

- Get Redis connection URL
- Returns: Redis connection URL

**`is_debug_mode() -> bool`**

- Check if debug mode is enabled
- Returns: `True` if debug mode is enabled

**`get_log_level() -> str`**

- Get log level
- Returns: Current log level

**`get_workspace_path() -> Path`**

- Get workspace path
- Returns: Path object for workspace

### 5. Main Launcher (`main.py`)

#### NexusPlatformLauncher Class

##### Methods

**`__init__(workspace_path: str = "/Users/Arief/Desktop/Nexus")`**

- Initialize the platform launcher
- Parameters:
  - `workspace_path`: Path to the workspace directory

**`async start_system()`**

- Start the complete system
- Initializes all components and runs interactive demo

**`async run_continuous_monitoring()`**

- Run continuous system monitoring
- Monitors system health and logs status

**`get_system_status() -> Dict[str, Any]`**

- Get current system status
- Returns: Dictionary with system status information

## Data Structures

### Financial Data Format

```python
{
    "expenses": [
        {
            "id": "exp1",
            "amount": 100.00,
            "date": datetime.now(),
            "description": "Office supplies"
        }
    ],
    "bank_statements": [
        {
            "id": "bank1",
            "amount": 100.00,
            "date": datetime.now(),
            "description": "Office supplies payment"
        }
    ]
}
```

### POV Analysis Format

```python
{
    "focus": "Financial reconciliation and analysis",
    "priority": "Data accuracy and fraud detection",
    "recommendations": ["Complete reconciliation", "Investigate discrepancies"]
}
```

### Theme Configuration Format

```python
{
    "name": "Financial Professional",
    "description": "Clean, professional design for financial professionals",
    "colors": {
        "primary": "#1e3a8a",
        "secondary": "#64748b",
        "background": "#ffffff",
        "text": "#1f2937"
    },
    "typography": {
        "font_family": "Inter, system-ui, sans-serif",
        "font_size_base": "16px",
        "font_weight_normal": "400",
        "font_weight_bold": "600"
    },
    "layout": {
        "type": "grid",
        "spacing": "1rem",
        "border_radius": "0.375rem"
    }
}
```

## Error Handling

All methods return appropriate success/failure indicators and log errors using the Python logging system. Error messages are descriptive and include context information.

## Logging

The system uses Python's built-in logging module with configurable log levels. Logs are written to both console and file (`nexus_platform.log`).

## Configuration

The system uses a centralized JSON configuration file (`config.json`) with the following main sections:

- `system`: Basic system configuration
- `database`: Database connection settings
- `redis`: Redis cache settings
- `ai_ml`: AI/ML model configuration
- `frontend`: Frontend theme and UI settings
- `security`: Security and authentication settings
- `monitoring`: Health monitoring configuration
- `ssot_integration`: SSOT integration settings
- `automation`: Automation and task scheduling settings
