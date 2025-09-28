# 🔧 Frenly AI - Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve common issues with the Frenly AI.

## Quick Diagnostics

### System Health Check

```bash
# Check if system is running
curl http://localhost:8080/api/status

# Check agent status
curl http://localhost:8080/api/agent/status

# Check system health
curl http://localhost:8080/api/health
```

### Log Analysis

```bash
# View recent logs
tail -n 50 nexus.log

# Search for errors
grep -i error nexus.log

# Search for warnings
grep -i warning nexus.log
```

## Common Issues

### 1. System Won't Start

#### Port Already in Use

**Symptoms:**

```
[Errno 48] error while attempting to bind on address ('127.0.0.1', 8080): address already in use
```

**Solutions:**

```bash
# Find process using port 8080
lsof -ti:8080

# Kill the process
lsof -ti:8080 | xargs kill -9

# Or use a different port
# Edit frenly_config.json and change port to 8081
```

#### Import Errors

**Symptoms:**

```
ModuleNotFoundError: No module named 'aiohttp'
ImportError: attempted relative import with no known parent package
```

**Solutions:**

```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"

# Verify virtual environment
which python
```

#### Permission Denied

**Symptoms:**

```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

```bash
# Fix file permissions
chmod +x frenly_simple.py
chmod 644 frenly_config.json

# Check directory permissions
ls -la frenly_simple.py
```

### 2. Web Interface Issues

#### Dashboard Won't Load

**Symptoms:**

- Blank page
- "Error loading dashboard" message
- 500 Internal Server Error

**Solutions:**

```bash
# Check if system is running
ps aux | grep frenly_simple.py

# Check port availability
netstat -tulpn | grep 8080

# Restart the system
pkill -f frenly_simple.py
python frenly_simple.py
```

#### Avatar Not Visible

**Symptoms:**

- Missing avatar in top-right corner
- Broken image icons

**Solutions:**

```bash
# Check static file serving
curl http://localhost:8080/static/avatar.png

# Verify file exists
ls -la static/avatar.png

# Check browser console for errors
# Open Developer Tools (F12) and check Console tab
```

#### Chat Not Working

**Symptoms:**

- Chat panel doesn't open
- Messages not sending
- "Method Not Allowed" errors

**Solutions:**

```bash
# Test chat API directly
curl -X POST http://localhost:8080/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Check WebSocket connection
# Open browser console and look for WebSocket errors
```

### 3. API Issues

#### 404 Not Found

**Symptoms:**

```
404: Not Found
```

**Solutions:**

```bash
# Check available endpoints
curl http://localhost:8080/api/status

# Verify endpoint exists
grep -r "api/status" frenly_simple.py

# Check URL spelling
curl http://localhost:8080/api/status  # Correct
curl http://localhost:8080/api/stat    # Incorrect
```

#### 500 Internal Server Error

**Symptoms:**

```
500: Internal Server Error
```

**Solutions:**

```bash
# Check logs for error details
tail -f nexus.log

# Check system resources
htop

# Restart the system
pkill -f frenly_simple.py
python frenly_simple.py
```

#### CORS Issues

**Symptoms:**

```
Access to fetch at 'http://localhost:8080/api/status' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**Solutions:**

```bash
# Check CORS configuration in frenly_simple.py
grep -r "CORS" frenly_simple.py

# Add CORS headers if missing
# The system should include CORS middleware
```

### 4. Agent Issues

#### Agent Not Responding

**Symptoms:**

- Agent status shows "inactive"
- Chat responses are empty
- Agent mood not updating

**Solutions:**

```bash
# Check agent status
curl http://localhost:8080/api/agent/status

# Restart the system
pkill -f frenly_simple.py
python frenly_simple.py

# Check agent initialization in logs
grep -i "agent" nexus.log
```

#### Personality Not Working

**Symptoms:**

- Agent responses are generic
- Mood not changing
- Personality traits not applied

**Solutions:**

```bash
# Check personality configuration
grep -A 10 "personality_traits" frenly_config.json

# Verify agent initialization
grep -i "personality" frenly_simple.py
```

### 5. Performance Issues

#### Slow Response Times

**Symptoms:**

- API calls take >5 seconds
- Web interface is sluggish
- High CPU usage

**Solutions:**

```bash
# Check system resources
htop
free -h
df -h

# Reduce max_workers in config
# Edit frenly_config.json
{
  "system": {
    "max_workers": 5
  }
}

# Check for memory leaks
ps aux | grep frenly_simple.py
```

#### High Memory Usage

**Symptoms:**

- System uses >1GB RAM
- Memory usage keeps growing
- System becomes unresponsive

**Solutions:**

```bash
# Monitor memory usage
watch -n 1 'ps aux | grep frenly_simple.py'

# Restart system periodically
# Add to crontab:
# 0 */6 * * * pkill -f frenly_simple.py && python frenly_simple.py &

# Check for memory leaks in code
```

#### CPU Usage Issues

**Symptoms:**

- CPU usage >80%
- System becomes slow
- High load average

**Solutions:**

```bash
# Check CPU usage
top -p $(pgrep frenly_simple.py)

# Reduce max_workers
# Edit frenly_config.json
{
  "system": {
    "max_workers": 3
  }
}

# Check for infinite loops in logs
grep -i "loop\|infinite" nexus.log
```

### 6. Configuration Issues

#### Invalid Configuration

**Symptoms:**

```
JSONDecodeError: Expecting ',' delimiter
KeyError: 'system'
```

**Solutions:**

```bash
# Validate JSON syntax
python -m json.tool frenly_config.json

# Check for missing keys
grep -r "system" frenly_config.json

# Use default configuration
cp frenly_config.json.example frenly_config.json
```

#### Configuration Not Loading

**Symptoms:**

- System uses default values
- Changes not applied
- Configuration file ignored

**Solutions:**

```bash
# Check file permissions
ls -la frenly_config.json

# Verify file path
grep -r "frenly_config.json" frenly_simple.py

# Check for syntax errors
python -c "import json; json.load(open('frenly_config.json'))"
```

### 7. Dependency Issues

#### NumPy Compatibility

**Symptoms:**

```
AttributeError: _ARRAY_API not found
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.2.6
```

**Solutions:**

```bash
# Install compatible NumPy version
pip install "numpy<2.0"

# Or install specific version
pip install numpy==1.26.4

# Reinstall related packages
pip install --force-reinstall scikit-learn pandas opencv-python
```

#### OpenCV Issues

**Symptoms:**

```
ImportError: libopencv_core.so.4.5: cannot open shared object file
```

**Solutions:**

```bash
# Install compatible OpenCV version
pip install "opencv-python<4.9"

# Or install specific version
pip install opencv-python==4.8.1.78

# Install system OpenCV if needed
# Ubuntu/Debian:
sudo apt install libopencv-dev
# macOS:
brew install opencv
```

#### Missing Dependencies

**Symptoms:**

```
ModuleNotFoundError: No module named 'aiohttp'
```

**Solutions:**

```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific package
pip install aiohttp

# Check virtual environment
which python
pip list
```

## Advanced Troubleshooting

### Debug Mode

Enable debug mode for detailed logging:

```json
{
  "system": {
    "debug": true,
    "log_level": "DEBUG"
  }
}
```

### Log Analysis

#### Parse Logs

```bash
# Extract error messages
grep -i "error" nexus.log | tail -20

# Extract warning messages
grep -i "warning" nexus.log | tail -20

# Extract specific patterns
grep -i "agent" nexus.log | tail -20
```

#### Log Rotation

```bash
# Set up log rotation
sudo nano /etc/logrotate.d/nexus
```

```
/opt/nexus/nexus.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 nexus nexus
}
```

### Network Troubleshooting

#### Port Scanning

```bash
# Check if port is open
nmap -p 8080 localhost

# Check if port is listening
netstat -tulpn | grep 8080

# Test port connectivity
telnet localhost 8080
```

#### Firewall Issues

```bash
# Check firewall status
sudo ufw status

# Allow port 8080
sudo ufw allow 8080

# Check iptables
sudo iptables -L
```

### System Monitoring

#### Resource Monitoring

```bash
# Monitor CPU and memory
htop

# Monitor disk usage
df -h

# Monitor network
iftop

# Monitor processes
ps aux | grep nexus
```

#### Performance Profiling

```bash
# Profile Python code
python -m cProfile frenly_simple.py

# Memory profiling
pip install memory_profiler
python -m memory_profiler frenly_simple.py
```

## Recovery Procedures

### System Recovery

#### Complete Reset

```bash
# Stop all processes
pkill -f frenly_simple.py

# Remove old files
rm -f nexus.log
rm -f *.pyc
rm -rf __pycache__

# Restore from backup
cp frenly_config.json.backup frenly_config.json

# Restart system
python frenly_simple.py
```

#### Data Recovery

```bash
# Backup current data
cp -r data/ data_backup_$(date +%Y%m%d)/

# Restore from backup
cp -r data_backup_20250920/ data/

# Verify data integrity
ls -la data/
```

### Configuration Recovery

#### Reset to Defaults

```bash
# Backup current config
cp frenly_config.json frenly_config.json.backup

# Restore default config
cp frenly_config.json.example frenly_config.json

# Restart system
pkill -f frenly_simple.py
python frenly_simple.py
```

## Prevention

### Regular Maintenance

#### Daily Checks

```bash
# Check system status
curl http://localhost:8080/api/status

# Check logs for errors
grep -i error nexus.log | tail -5

# Check disk space
df -h
```

#### Weekly Maintenance

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Clean old logs
find . -name "*.log" -mtime +7 -delete

# Backup configuration
cp frenly_config.json frenly_config.json.$(date +%Y%m%d)
```

#### Monthly Maintenance

```bash
# Full system restart
pkill -f frenly_simple.py
python frenly_simple.py

# Check for updates
git pull origin main

# Review logs
grep -i "error\|warning" nexus.log | wc -l
```

### Monitoring Setup

#### Health Check Script

```bash
#!/bin/bash
# health_check.sh

# Check if system is running
if ! curl -s http://localhost:8080/api/status > /dev/null; then
    echo "Frenly is down! Restarting..."
    pkill -f frenly_simple.py
    python frenly_simple.py &
    sleep 5
fi
```

#### Cron Job

```bash
# Add to crontab
crontab -e

# Add this line to check every 5 minutes
*/5 * * * * /path/to/health_check.sh
```

## Getting Help

### Self-Help Resources

1. **Check Documentation**: Review README, API docs, and guides
2. **Search Logs**: Look for error messages in logs
3. **Test Components**: Test individual components separately
4. **Check Configuration**: Verify configuration syntax and values

### Community Support

1. **GitHub Issues**: Create an issue with detailed information
2. **Discussion Forums**: Ask questions in community forums
3. **Documentation**: Check if issue is documented
4. **Code Review**: Review code for obvious issues

### Professional Support

1. **Enterprise Support**: Contact for enterprise support
2. **Consulting**: Hire consultants for complex issues
3. **Training**: Attend training sessions
4. **Custom Development**: Request custom features

## Issue Reporting

### When Reporting Issues

Include the following information:

1. **System Information**:
   - Operating System and version
   - Python version
   - Architecture (x86_64, ARM, etc.)

2. **Error Details**:
   - Complete error message
   - Stack trace
   - Log file excerpts

3. **Steps to Reproduce**:
   - What you were doing
   - Commands you ran
   - Configuration changes

4. **Environment**:
   - Virtual environment details
   - Installed packages
   - Configuration file contents

### Issue Template

```markdown
## Issue Description

Brief description of the issue

## System Information

- OS: macOS 14.0
- Python: 3.11.5
- Architecture: x86_64

## Error Message
```

Complete error message here

```

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Log Files
```

Relevant log excerpts

````

## Configuration
```json
{
  "system": {
    "debug": true
  }
}
````

```

---

**Troubleshooting Guide v4.0.0**
*Last updated: September 20, 2025*
```
