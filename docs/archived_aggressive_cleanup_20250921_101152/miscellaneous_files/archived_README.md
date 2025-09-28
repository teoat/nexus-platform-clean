# NEXUS Tier 5 Launcher - Enhanced Edition

A comprehensive service management platform with advanced monitoring, security, high availability, and operational features.

## 🚀 Features

### Core Features

- **Service Management**: Start, stop, restart, and monitor services
- **Real-time Dashboard**: Web-based control panel with live updates
- **Health Monitoring**: Automated health checks and service status tracking
- **WebSocket Support**: Real-time communication for live updates

### Enhanced Features

- **Structured Logging**: JSON-formatted logs with rotation and multiple levels
- **Distributed Tracing**: OpenTelemetry integration with Jaeger support
- **Comprehensive Monitoring**: Prometheus metrics and Grafana-ready dashboards
- **Security Features**: Authentication, authorization, rate limiting, and CORS
- **High Availability**: Circuit breakers, load balancing, and auto-failover
- **Operational Tools**: Backup/restore, deployment management, and configuration snapshots

## 📋 Prerequisites

- Go 1.24.5 or later
- Docker (for service management)
- Jaeger (for distributed tracing) - optional
- Prometheus (for metrics collection) - optional

## 🛠️ Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd tools/utilities/tools/utilities/nexus_tier5_launcher
   ```

2. **Install dependencies**:

   ```bash
   go mod tidy
   ```

3. **Configure the launcher**:

   ```bash
   cp config.yml.example config.yml
   # Edit config.yml with your settings
   ```

4. **Build the launcher**:
   ```bash
   go build -o tools/utilities/tools/utilities/nexus_tier5_launcher
   ```

## ⚙️ Configuration

### Basic Configuration (config.yml)

```yaml
services:
  - name: "tools/utilities/tools/utilities/nexus-backend"
    command: "docker run -p 8001:8000 tools/utilities/tools/utilities/nexus-backend"
    health_check: "http://localhost:8001/health"
    port: 8001
    priority: 1
    auto_restart: true
    max_retries: 3
    restart_delay: 30s

panel:
  title: "NEXUS Tier5 Control Panel"
  theme: "dark"
  port: 8080
  refresh_rate: 5
  features:
    service_management: true
    log_viewer: true
    health_monitoring: true
    performance_stats: true
    customization: true

user_profile:
  name: "Admin User"
  email: "admin@tools/utilities/tools/utilities/nexus.local"
  preferences:
    theme: "dark"
    notifications: "enabled"
  dashboard:
    layout: "grid"
    widgets: ["services", "metrics", "logs"]
    theme: "dark"
    auto_refresh: true

logging:
  level: "info"
  file: ".tools/utilities/tools/utilities/nexus/logs/app.log"
  max_size: 100
```

### Environment Variables

```bash
# JWT Secret for authentication (auto-generated if not set)
export JWT_SECRET="your-secret-key"

# Jaeger endpoint for distributed tracing
export JAEGER_ENDPOINT="http://localhost:14268/api/traces"

# Log level
export LOG_LEVEL="info"
```

## 🚀 Usage

### Starting the Launcher

```bash
./NEXUS_nexus_backend/tools/utilities/tools/utilities/nexus_tier5_launcher
```

### Accessing the Dashboard

- **Control Panel**: http://localhost:8080
- **Metrics**: http://localhost:8080/metrics
- **Health Check**: http://localhost:8080/health
- **API Health**: http://localhost:8080/api/health

### API Endpoints

#### Service Management

- `GET /api/status` - Get overall system status
- `GET /api/services` - List all services
- `POST /api/services/{name}/start` - Start a service
- `POST /api/services/{name}/stop` - Stop a service
- `POST /api/services/{name}/restart` - Restart a service

#### Monitoring

- `GET /api/monitoring` - Get monitoring dashboard data
- `GET /api/alerts` - Get current alerts
- `GET /metrics` - Prometheus metrics

#### Operations

- `GET /api/backups` - List backups
- `POST /api/backups` - Create backup
- `POST /api/backups/{id}/restore` - Restore backup
- `GET /api/deployments` - List deployments
- `POST /api/deployments` - Create deployment

#### Security

- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/status` - Check authentication status

## 🔧 Advanced Features

### Structured Logging

The launcher uses structured JSON logging with multiple log levels:

```go
// Log service events
AppLogger.LogServiceStart("my-service", "docker run my-service")
AppLogger.LogServiceHealth("my-service", true, 150*time.Millisecond)
AppLogger.LogServiceRestart("my-service", 3, "health_check_failed")

// Log security events
AppLogger.LogSecurityEvent("failed_login", map[string]interface{}{
    "ip": "192.168.1.100",
    "username": "admin",
})
```

### Distributed Tracing

Tracing is automatically integrated into all service operations:

```go
// Create spans for operations
ctx, span := TraceServiceOperation(ctx, "start", "my-service")
defer span.End()

// Add attributes to spans
AddSpanAttributes(span, map[string]interface{}{
    "service.command": "docker run my-service",
    "service.port": 8001,
})
```

### Monitoring and Metrics

The launcher exposes comprehensive Prometheus metrics:

- **Service Metrics**: Status, uptime, restart count, health checks
- **System Metrics**: CPU, memory, disk usage
- **API Metrics**: Request count, duration, response size
- **Security Metrics**: Failed logins, rate limit hits, security events
- **Business Metrics**: Active connections, service counts

### High Availability Features

#### Circuit Breakers

```go
// Create circuit breaker for service calls
circuitBreaker := NewCircuitBreaker(3, 30*time.Second)

// Execute with circuit breaker protection
err := circuitBreaker.Call(func() error {
    return callExternalService()
})
```

#### Load Balancing

```go
// Create load balancer
lb := NewLoadBalancer("my-service", []string{
    "http://service1:8001",
    "http://service2:8001",
}, RoundRobin)

// Get next endpoint
endpoint := lb.GetNextEndpoint()
```

#### Auto-failover

```go
// Create failover manager
fm := NewFailoverManager("my-service",
    "http://primary:8001",
    []string{"http://backup1:8001", "http://backup2:8001"})

// Failover to backup
err := fm.Failover()
```

### Security Features

#### Authentication

```go
// Create user session
session, err := Security.CreateSession("user123", "admin", "192.168.1.100", "Mozilla/5.0...")

// Validate session
session, valid := Security.ValidateSession(sessionID)
```

#### Rate Limiting

```go
// Check rate limit
if !Security.CheckRateLimit("192.168.1.100") {
    return errors.New("rate limit exceeded")
}
```

#### JWT Tokens

```go
// Generate JWT token
token, err := Security.GenerateJWT("user123", "admin", "admin")

// Validate JWT token
claims, err := Security.ValidateJWT(tokenString)
```

### Operational Tools

#### Backup Management

```go
// Create backup
backup, err := Operations.CreateBackup("full", "Scheduled backup")

// Restore backup
err := Operations.RestoreBackup(backupID)

// List backups
backups, err := Operations.ListBackups()
```

#### Deployment Management

```go
// Create deployment
deployment, err := Operations.CreateDeployment("v1.2.3", "production",
    []string{"service1", "service2"}, config)

// Update deployment status
err := Operations.UpdateDeploymentStatus(deploymentID, "completed")
```

#### Configuration Snapshots

```go
// Create configuration snapshot
snapshot, err := Operations.CreateConfigurationSnapshot()
```

## 📊 Monitoring Dashboard

The monitoring dashboard provides:

- **Service Status**: Real-time status of all services
- **System Metrics**: CPU, memory, disk usage graphs
- **Alerts**: Current alerts and notifications
- **Performance**: Response times and throughput
- **Logs**: Real-time log streaming
- **Health Checks**: Service health status

## 🔒 Security Considerations

### Authentication

- Default credentials: admin/admin (change in production)
- Session-based authentication with secure cookies
- JWT tokens for API access

### Rate Limiting

- 100 requests per minute per IP
- Automatic IP blocking after 5 failed login attempts
- Configurable rate limits per endpoint

### Security Headers

- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000

### CORS

- Configurable CORS policies
- Support for credentials
- Preflight request handling

## 🚨 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Check port usage: `netstat -tulpn | grep :8080`
   - Update port in config.yml if needed

2. **Service Health Checks Failing**
   - Verify service endpoints are accessible
   - Check service logs for errors
   - Adjust health check timeout if needed

3. **Authentication Issues**
   - Verify JWT_SECRET is set
   - Check session cookies are enabled
   - Clear browser cookies and try again

4. **Metrics Not Appearing**
   - Ensure Prometheus is running
   - Check /metrics endpoint is accessible
   - Verify metric collection is enabled

### Logs

Logs are stored in `.tools/utilities/tools/utilities/nexus/logs/`:

- `app.log` - Application logs
- `services.log` - Service-specific logs
- `access.log` - HTTP access logs
- `errors.log` - Error logs

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL="debug"
./NEXUS_nexus_backend/tools/utilities/tools/utilities/nexus_tier5_launcher
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the logs for error details

## 🔄 Changelog

### v1.0.0

- Initial release with basic service management
- Added structured logging
- Implemented distributed tracing
- Added comprehensive monitoring
- Integrated security features
- Added high availability features
- Implemented operational tools
- Created comprehensive documentation
