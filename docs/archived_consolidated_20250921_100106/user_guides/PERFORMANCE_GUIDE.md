# ⚡ Frenly AI - Performance Guide

## Overview

This guide provides comprehensive information about optimizing the performance of the Frenly AI for different use cases and environments.

## Performance Metrics

### Key Performance Indicators (KPIs)

#### Response Time

- **API Response Time**: < 100ms for simple requests
- **Web Interface Load Time**: < 2 seconds
- **Agent Response Time**: < 500ms for chat messages
- **Task Processing Time**: Varies by task complexity

#### Throughput

- **Concurrent Users**: 100+ simultaneous users
- **API Requests per Second**: 1000+ requests/second
- **Task Processing Rate**: 100+ tasks/minute
- **WebSocket Connections**: 500+ concurrent connections

#### Resource Usage

- **CPU Usage**: < 50% under normal load
- **Memory Usage**: < 1GB for typical workloads
- **Disk I/O**: Minimal for most operations
- **Network Bandwidth**: < 10Mbps for typical usage

## Performance Optimization

### System-Level Optimization

#### CPU Optimization

```json
{
  "system": {
    "max_workers": 10,
    "task_timeout": 3600,
    "retry_attempts": 3
  }
}
```

**Recommendations:**

- Set `max_workers` to 2x CPU cores for I/O-bound tasks
- Set `max_workers` to CPU cores for CPU-bound tasks
- Use `task_timeout` to prevent hanging tasks
- Implement proper retry logic

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

**Recommendations:**

- Reduce `max_workers` for memory-constrained environments
- Implement memory monitoring
- Use generators for large datasets
- Clear unused variables and objects

#### Disk I/O Optimization

```json
{
  "system": {
    "log_level": "WARNING",
    "debug": false
  },
  "monitoring": {
    "metrics_interval": 60
  }
}
```

**Recommendations:**

- Reduce logging frequency
- Use async I/O operations
- Implement log rotation
- Cache frequently accessed data

### Application-Level Optimization

#### Async/Await Patterns

```python
# Good: Async operations
async def process_task(task):
    result = await some_async_operation(task)
    return result

# Bad: Blocking operations
def process_task(task):
    result = some_blocking_operation(task)
    return result
```

#### Caching Strategies

```python
# Implement caching for expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_calculation(data):
    # Expensive computation
    return result

# Use Redis for distributed caching
import redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_cached_data(key):
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None
```

#### Database Optimization

```python
# Use connection pooling
import asyncpg

async def create_db_pool():
    return await asyncpg.create_pool(
        host='localhost',
        port=5432,
        database='nexus',
        user='nexus',
        password='password',
        min_size=5,
        max_size=20
    )

# Use prepared statements
async def get_task(task_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            'SELECT * FROM tasks WHERE id = $1',
            task_id
        )
```

### Web Interface Optimization

#### Frontend Performance

```html
<!-- Optimize HTML structure -->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Frenly Dashboard</title>
    <!-- Minify CSS and JS -->
    <link rel="stylesheet" href="/static/css/dashboard.min.css" />
    <script src="/static/js/dashboard.min.js" defer></script>
  </head>
  <body>
    <!-- Use semantic HTML -->
    <main id="dashboard">
      <!-- Content -->
    </main>
  </body>
</html>
```

#### JavaScript Optimization

```javascript
// Use efficient DOM manipulation
const dashboard = document.getElementById("dashboard");

// Debounce API calls
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Debounced API call
const debouncedUpdate = debounce(updateDashboard, 300);

// Use requestAnimationFrame for animations
function animateElement(element) {
  requestAnimationFrame(() => {
    element.style.transform = "translateX(100px)";
  });
}
```

#### CSS Optimization

```css
/* Use efficient selectors */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

/* Use CSS transforms for animations */
.avatar {
  transition: transform 0.3s ease;
}

.avatar:hover {
  transform: scale(1.1);
}

/* Use CSS variables for theming */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
  --danger-color: #dc3545;
}
```

### API Optimization

#### Response Caching

```python
# Implement response caching
from functools import wraps
import hashlib
import json

def cache_response(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key
            key = hashlib.md5(
                f"{func.__name__}:{str(args)}:{str(kwargs)}".encode()
            ).hexdigest()

            # Check cache
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Use caching decorator
@cache_response(ttl=60)
async def get_system_status():
    return {"status": "running", "uptime": 3600}
```

#### Request Batching

```python
# Implement request batching
class RequestBatcher:
    def __init__(self, batch_size=10, timeout=0.1):
        self.batch_size = batch_size
        self.timeout = timeout
        self.pending_requests = []
        self.batch_tasks = {}

    async def add_request(self, request_id, request_data):
        self.pending_requests.append((request_id, request_data))

        if len(self.pending_requests) >= self.batch_size:
            await self.process_batch()

    async def process_batch(self):
        if not self.pending_requests:
            return

        # Process batch
        batch_results = await process_batch_requests(self.pending_requests)

        # Resolve individual requests
        for (request_id, _), result in zip(self.pending_requests, batch_results):
            if request_id in self.batch_tasks:
                self.batch_tasks[request_id].set_result(result)

        self.pending_requests.clear()
```

#### Connection Pooling

```python
# Use connection pooling for external services
import aiohttp

class HTTPClient:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        self.session = aiohttp.ClientSession(connector=connector)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(self, url, **kwargs):
        async with self.session.get(url, **kwargs) as response:
            return await response.json()
```

## Monitoring and Profiling

### Performance Monitoring

#### System Metrics

```python
import psutil
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}

    def collect_metrics(self):
        """Collect system performance metrics"""
        self.metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters()._asdict(),
            'timestamp': time.time()
        }
        return self.metrics

    def get_performance_score(self):
        """Calculate overall performance score"""
        cpu_score = max(0, 100 - self.metrics['cpu_percent'])
        memory_score = max(0, 100 - self.metrics['memory_percent'])
        disk_score = max(0, 100 - self.metrics['disk_usage'])

        return (cpu_score + memory_score + disk_score) / 3
```

#### Application Metrics

```python
import time
from functools import wraps

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'request_duration': [],
            'error_count': 0,
            'active_connections': 0
        }

    def track_request(self, func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            self.metrics['request_count'] += 1

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                self.metrics['error_count'] += 1
                raise
            finally:
                duration = time.time() - start_time
                self.metrics['request_duration'].append(duration)

        return wrapper

    def get_average_response_time(self):
        if not self.metrics['request_duration']:
            return 0
        return sum(self.metrics['request_duration']) / len(self.metrics['request_duration'])
```

### Profiling Tools

#### CPU Profiling

```python
import cProfile
import pstats

def profile_function(func):
    """Profile a function's CPU usage"""
    profiler = cProfile.Profile()
    profiler.enable()

    result = func()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions

    return result
```

#### Memory Profiling

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    """Function that uses a lot of memory"""
    data = []
    for i in range(1000000):
        data.append(i * 2)
    return data

# Run with: python -m memory_profiler script.py
```

#### Line-by-Line Profiling

```python
from line_profiler import LineProfiler

def profile_lines(func):
    """Profile function line by line"""
    profiler = LineProfiler()
    profiler.add_function(func)
    profiler.enable()

    result = func()

    profiler.disable()
    profiler.print_stats()

    return result
```

## Load Testing

### Load Testing Tools

#### Using Apache Bench (ab)

```bash
# Test API endpoints
ab -n 1000 -c 10 http://localhost:8080/api/status

# Test with different concurrency levels
ab -n 1000 -c 50 http://localhost:8080/api/agent/chat

# Test with POST requests
ab -n 100 -c 10 -p post_data.json -T application/json http://localhost:8080/api/tasks
```

#### Using wrk

```bash
# Basic load test
wrk -t12 -c400 -d30s http://localhost:8080/api/status

# Test with Lua script
wrk -t12 -c400 -d30s -s script.lua http://localhost:8080/api/agent/chat
```

#### Custom Load Testing

```python
import asyncio
import aiohttp
import time

async def load_test():
    """Custom load testing function"""
    async with aiohttp.ClientSession() as session:
        tasks = []

        # Create 100 concurrent requests
        for i in range(100):
            task = asyncio.create_task(
                session.get('http://localhost:8080/api/status')
            )
            tasks.append(task)

        # Wait for all requests to complete
        start_time = time.time()
        responses = await asyncio.gather(*tasks)
        end_time = time.time()

        # Calculate metrics
        total_time = end_time - start_time
        successful_requests = sum(1 for r in responses if r.status == 200)

        print(f"Total requests: {len(tasks)}")
        print(f"Successful requests: {successful_requests}")
        print(f"Total time: {total_time:.2f}s")
        print(f"Requests per second: {len(tasks) / total_time:.2f}")

# Run load test
asyncio.run(load_test())
```

## Scaling Strategies

### Horizontal Scaling

#### Load Balancing

```nginx
# Nginx configuration for load balancing
upstream nexus_backend {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;
    server 127.0.0.1:8082;
}

server {
    listen 80;
    server_name nexus.example.com;

    location / {
        proxy_pass http://nexus_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### Multiple Instances

```bash
# Run multiple instances on different ports
python frenly_simple.py --port 8080 &
python frenly_simple.py --port 8081 &
python frenly_simple.py --port 8082 &
```

### Vertical Scaling

#### Resource Allocation

```json
{
  "system": {
    "max_workers": 20,
    "task_timeout": 7200,
    "retry_attempts": 5
  },
  "monitoring": {
    "metrics_interval": 5,
    "health_check_interval": 10
  }
}
```

#### Memory Optimization

```python
# Implement memory-efficient data structures
from collections import deque
import gc

class MemoryEfficientQueue:
    def __init__(self, maxsize=1000):
        self.queue = deque(maxlen=maxsize)
        self.maxsize = maxsize

    def put(self, item):
        self.queue.append(item)

    def get(self):
        return self.queue.popleft() if self.queue else None

    def cleanup(self):
        """Clean up unused memory"""
        gc.collect()
```

## Performance Tuning

### Database Performance

#### Query Optimization

```python
# Use indexes for frequently queried fields
CREATE INDEX idx_task_status ON tasks(status);
CREATE INDEX idx_task_created_at ON tasks(created_at);

# Use prepared statements
async def get_tasks_by_status(status):
    async with pool.acquire() as conn:
        return await conn.fetch(
            'SELECT * FROM tasks WHERE status = $1 ORDER BY created_at DESC',
            status
        )

# Use pagination for large datasets
async def get_tasks_paginated(offset=0, limit=100):
    async with pool.acquire() as conn:
        return await conn.fetch(
            'SELECT * FROM tasks ORDER BY created_at DESC LIMIT $1 OFFSET $2',
            limit, offset
        )
```

#### Connection Pooling

```python
# Configure connection pool
async def create_optimized_pool():
    return await asyncpg.create_pool(
        host='localhost',
        port=5432,
        database='nexus',
        user='nexus',
        password='password',
        min_size=10,
        max_size=50,
        max_queries=50000,
        max_inactive_connection_lifetime=300.0
    )
```

### Caching Strategies

#### Redis Caching

```python
import redis
import json
import pickle

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    async def get(self, key):
        """Get value from cache"""
        value = self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key, value, ttl=300):
        """Set value in cache with TTL"""
        self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key):
        """Delete value from cache"""
        self.redis.delete(key)
```

#### In-Memory Caching

```python
from functools import lru_cache
import time

class InMemoryCache:
    def __init__(self, maxsize=1000, ttl=300):
        self.cache = {}
        self.maxsize = maxsize
        self.ttl = ttl

    def get(self, key):
        """Get value from cache"""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def set(self, key, value):
        """Set value in cache"""
        if len(self.cache) >= self.maxsize:
            # Remove oldest entry
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]

        self.cache[key] = (value, time.time())
```

## Best Practices

### Code Optimization

#### Efficient Algorithms

```python
# Use efficient data structures
from collections import defaultdict, Counter

# Good: O(1) average case
def count_items_efficient(items):
    return Counter(items)

# Bad: O(n²) worst case
def count_items_inefficient(items):
    counts = {}
    for item in items:
        if item in counts:
            counts[item] += 1
        else:
            counts[item] = 1
    return counts
```

#### Memory Management

```python
# Use generators for large datasets
def process_large_dataset(data):
    for item in data:
        yield process_item(item)

# Use context managers for resources
async def process_file(filename):
    async with aiofiles.open(filename, 'r') as f:
        async for line in f:
            yield process_line(line)
```

#### Error Handling

```python
# Implement proper error handling
async def robust_api_call(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()
        except aiohttp.ClientError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Configuration Optimization

#### Environment-Specific Settings

```json
{
  "development": {
    "system": {
      "max_workers": 2,
      "debug": true,
      "log_level": "DEBUG"
    }
  },
  "production": {
    "system": {
      "max_workers": 20,
      "debug": false,
      "log_level": "WARNING"
    }
  }
}
```

#### Dynamic Configuration

```python
# Load configuration based on environment
import os

def load_config():
    env = os.getenv('NEXUS_ENV', 'development')

    with open(f'config_{env}.json', 'r') as f:
        config = json.load(f)

    # Override with environment variables
    config['system']['max_workers'] = int(
        os.getenv('NEXUS_MAX_WORKERS', config['system']['max_workers'])
    )

    return config
```

## Performance Monitoring Dashboard

### Real-time Metrics

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Performance Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  </head>
  <body>
    <div class="metrics-grid">
      <div class="metric-card">
        <h3>CPU Usage</h3>
        <canvas id="cpuChart"></canvas>
      </div>
      <div class="metric-card">
        <h3>Memory Usage</h3>
        <canvas id="memoryChart"></canvas>
      </div>
      <div class="metric-card">
        <h3>Response Time</h3>
        <canvas id="responseChart"></canvas>
      </div>
    </div>

    <script>
      // Real-time performance monitoring
      const charts = {
        cpu: new Chart(document.getElementById("cpuChart"), {
          type: "line",
          data: { labels: [], datasets: [{ data: [] }] },
          options: { responsive: true },
        }),
        memory: new Chart(document.getElementById("memoryChart"), {
          type: "line",
          data: { labels: [], datasets: [{ data: [] }] },
          options: { responsive: true },
        }),
        response: new Chart(document.getElementById("responseChart"), {
          type: "line",
          data: { labels: [], datasets: [{ data: [] }] },
          options: { responsive: true },
        }),
      };

      // Update charts every 5 seconds
      setInterval(updateMetrics, 5000);

      async function updateMetrics() {
        const response = await fetch("/api/metrics");
        const metrics = await response.json();

        // Update CPU chart
        charts.cpu.data.labels.push(new Date().toLocaleTimeString());
        charts.cpu.data.datasets[0].data.push(metrics.cpu_percent);
        charts.cpu.update();

        // Update memory chart
        charts.memory.data.labels.push(new Date().toLocaleTimeString());
        charts.memory.data.datasets[0].data.push(metrics.memory_percent);
        charts.memory.update();

        // Update response time chart
        charts.response.data.labels.push(new Date().toLocaleTimeString());
        charts.response.data.datasets[0].data.push(metrics.avg_response_time);
        charts.response.update();
      }
    </script>
  </body>
</html>
```

---

**Performance Guide v4.0.0**  
_Last updated: September 20, 2025_
