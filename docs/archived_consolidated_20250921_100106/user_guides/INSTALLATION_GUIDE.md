# 🚀 Frenly AI - Installation Guide

## Overview

This guide provides step-by-step instructions for installing and setting up the Frenly AI on various platforms.

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: macOS, Linux, or Windows
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Storage**: 500MB free space
- **Network**: Internet connection for dependency installation

### Required Software

- **Python 3.8+**: [Download Python](https://www.python.org/downloads/)
- **pip**: Python package manager (usually included with Python)
- **Git**: [Download Git](https://git-scm.com/downloads) (optional, for cloning)

## Installation Methods

### Method 1: Direct Installation (Recommended)

#### Step 1: Download the System

```bash
# Clone the repository (if using Git)
git clone <repository-url>
cd frenly_ai

# OR download and extract the ZIP file
# Extract to your desired location
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv nexus_env

# Activate virtual environment
# On macOS/Linux:
source nexus_env/bin/activate

# On Windows:
nexus_env\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

#### Step 4: Configure the System

```bash
# Copy the example configuration
cp frenly_config.json.example frenly_config.json

# Edit the configuration file
nano frenly_config.json
```

#### Step 5: Test the Installation

```bash
# Test the system
python frenly_simple.py
```

### Method 2: Docker Installation

#### Step 1: Install Docker

- **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)

#### Step 2: Build the Docker Image

```bash
# Build the Docker image
docker build -t nexus-unified-system .
```

#### Step 3: Run the Container

```bash
# Run the container
docker run -p 8080:8080 -v $(pwd)/frenly_config.json:/app/frenly_config.json nexus-unified-system
```

### Method 3: Package Installation

#### Step 1: Install from PyPI (Future)

```bash
# Install the package (when available)
pip install nexus-unified-system
```

#### Step 2: Initialize the System

```bash
# Initialize the system
nexus-init
```

## Platform-Specific Instructions

### macOS Installation

#### Using Homebrew (Recommended)

```bash
# Install Python
brew install python@3.11

# Install dependencies
pip3 install -r requirements.txt

# Run the system
python3 frenly_simple.py
```

#### Using MacPorts

```bash
# Install Python
sudo port install python311

# Install dependencies
pip-3.11 install -r requirements.txt

# Run the system
python3.11 frenly_simple.py
```

### Linux Installation

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Create virtual environment
python3 -m venv nexus_env
source nexus_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the system
python frenly_simple.py
```

#### CentOS/RHEL/Fedora

```bash
# Install Python and pip
sudo yum install python3 python3-pip
# OR on newer versions:
sudo dnf install python3 python3-pip

# Create virtual environment
python3 -m venv nexus_env
source nexus_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the system
python frenly_simple.py
```

#### Arch Linux

```bash
# Install Python and pip
sudo pacman -S python python-pip

# Create virtual environment
python -m venv nexus_env
source nexus_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the system
python frenly_simple.py
```

### Windows Installation

#### Using Python.org Installer

1. **Download Python**: Go to [python.org](https://www.python.org/downloads/)
2. **Run Installer**: Run the downloaded installer
3. **Check "Add to PATH"**: Make sure to check this option
4. **Install pip**: pip should be included automatically

#### Using Anaconda/Miniconda

```bash
# Create conda environment
conda create -n nexus python=3.11

# Activate environment
conda activate nexus

# Install dependencies
pip install -r requirements.txt

# Run the system
python frenly_simple.py
```

#### Using Chocolatey

```bash
# Install Python
choco install python

# Install dependencies
pip install -r requirements.txt

# Run the system
python frenly_simple.py
```

## Configuration

### Basic Configuration

Edit `frenly_config.json`:

```json
{
  "system": {
    "name": "Frenly AI",
    "version": "4.0.0",
    "debug": false,
    "log_level": "INFO",
    "max_workers": 10,
    "task_timeout": 3600,
    "retry_attempts": 3
  },
  "agent": {
    "name": "Frenly",
    "personality": "friendly",
    "response_delay": 0.1,
    "learning_enabled": true
  },
  "web": {
    "host": "localhost",
    "port": 8080,
    "enable_websockets": true
  }
}
```

### Advanced Configuration

#### Environment Variables

```bash
# Set environment variables
export NEXUS_DEBUG=false
export NEXUS_PORT=8080
export NEXUS_LOG_LEVEL=INFO
```

#### Custom Configuration

```json
{
  "system": {
    "name": "My Frenly System",
    "debug": true,
    "log_level": "DEBUG",
    "max_workers": 20
  },
  "agent": {
    "name": "MyAI",
    "personality": "professional",
    "response_delay": 0.5
  },
  "web": {
    "host": "0.0.0.0",
    "port": 9000,
    "enable_websockets": true
  },
  "monitoring": {
    "enabled": true,
    "metrics_interval": 5,
    "health_check_interval": 15
  }
}
```

## Verification

### Test the Installation

#### 1. Check System Status

```bash
# Test system startup
python frenly_simple.py

# In another terminal, test API
curl http://localhost:8080/api/status
```

#### 2. Test Web Interface

1. Open browser to http://localhost:8080
2. Verify dashboard loads
3. Check agent avatar is visible
4. Test chat functionality

#### 3. Test API Endpoints

```bash
# Test system status
curl http://localhost:8080/api/status

# Test agent status
curl http://localhost:8080/api/agent/status

# Test chat
curl -X POST http://localhost:8080/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Frenly!"}'
```

## Troubleshooting

### Common Issues

#### Port Already in Use

```bash
# Find process using port 8080
lsof -ti:8080

# Kill the process
lsof -ti:8080 | xargs kill -9

# Or use a different port
# Edit frenly_config.json and change port to 8081
```

#### Permission Denied

```bash
# Fix file permissions
chmod +x frenly_simple.py
chmod 644 frenly_config.json

# Or run with sudo (not recommended)
sudo python frenly_simple.py
```

#### Import Errors

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Install missing dependencies
pip install -r requirements.txt

# Check virtual environment
which python
```

#### Memory Issues

```bash
# Check memory usage
free -h

# Reduce max_workers in config
# Edit frenly_config.json and set max_workers to 5
```

### Dependency Issues

#### NumPy Compatibility

```bash
# Install compatible NumPy version
pip install "numpy<2.0"

# Or install specific version
pip install numpy==1.26.4
```

#### OpenCV Issues

```bash
# Install compatible OpenCV version
pip install "opencv-python<4.9"

# Or install specific version
pip install opencv-python==4.8.1.78
```

#### Missing Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Or install individually
pip install aiohttp psutil numpy scikit-learn opencv-python
```

## Performance Optimization

### System Tuning

#### Memory Optimization

```json
{
  "system": {
    "max_workers": 5,
    "task_timeout": 1800
  },
  "monitoring": {
    "metrics_interval": 30
  }
}
```

#### CPU Optimization

```json
{
  "system": {
    "max_workers": 10,
    "task_timeout": 3600
  },
  "agent": {
    "response_delay": 0.1
  }
}
```

### Production Deployment

#### Using systemd (Linux)

```bash
# Create systemd service file
sudo nano /etc/systemd/system/nexus.service
```

```ini
[Unit]
Description=Frenly AI
After=network.target

[Service]
Type=simple
User=nexus
WorkingDirectory=/opt/nexus
ExecStart=/opt/nexus/venv/bin/python frenly_simple.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable nexus
sudo systemctl start nexus
```

#### Using Docker Compose

```yaml
version: "3.8"
services:
  nexus:
    build: .
    ports:
      - "8080:8080"
    environment:
      - NEXUS_DEBUG=false
      - NEXUS_PORT=8080
    volumes:
      - ./frenly_config.json:/app/frenly_config.json
    restart: unless-stopped
```

## Security Considerations

### Basic Security

#### Firewall Configuration

```bash
# Allow only local connections
# Edit frenly_config.json
{
  "web": {
    "host": "127.0.0.1",
    "port": 8080
  }
}
```

#### API Key Protection

```json
{
  "security": {
    "api_key_required": true,
    "api_key": "your-secure-api-key"
  }
}
```

### Advanced Security

#### SSL/TLS Configuration

```json
{
  "web": {
    "ssl_enabled": true,
    "ssl_cert": "/path/to/cert.pem",
    "ssl_key": "/path/to/key.pem"
  }
}
```

#### Authentication

```json
{
  "security": {
    "enable_auth": true,
    "auth_method": "jwt",
    "jwt_secret": "your-jwt-secret"
  }
}
```

## Maintenance

### Regular Maintenance

#### Update Dependencies

```bash
# Update all dependencies
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade aiohttp
```

#### Backup Configuration

```bash
# Backup configuration
cp frenly_config.json frenly_config.json.backup

# Backup data
cp -r data/ data_backup/
```

#### Log Management

```bash
# View logs
tail -f nexus.log

# Rotate logs
logrotate nexus.log
```

### Monitoring

#### Health Checks

```bash
# Check system health
curl http://localhost:8080/api/health

# Check system status
curl http://localhost:8080/api/status
```

#### Performance Monitoring

```bash
# Monitor system resources
htop

# Monitor network
netstat -tulpn | grep 8080
```

## Uninstallation

### Complete Removal

```bash
# Stop the system
pkill -f frenly_simple.py

# Remove virtual environment
rm -rf nexus_env

# Remove system files
rm -rf frenly_ai/

# Remove configuration
rm -f frenly_config.json
```

### Partial Removal

```bash
# Stop the system
pkill -f frenly_simple.py

# Remove only data
rm -rf data/

# Keep configuration and code
```

## Support

### Getting Help

- **Documentation**: Check the comprehensive guides
- **Issues**: Create an issue in the repository
- **Community**: Join the discussion forums
- **Email**: Contact the development team

### Reporting Issues

When reporting installation issues, please include:

1. **Operating System**: Version and architecture
2. **Python Version**: `python --version`
3. **Error Messages**: Complete error output
4. **Steps Taken**: What you tried
5. **Log Files**: Relevant log files

---

**Installation Guide v4.0.0**  
_Last updated: September 20, 2025_
