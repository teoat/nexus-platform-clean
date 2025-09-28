# 🤖 **FRENLY AI - INTEGRATION GUIDE**

## 📋 **QUICK START**

### **1. Prerequisites**

- Node.js 18+
- Python 3.9+
- Docker & Docker Compose
- LLM API keys (OpenAI, Anthropic, etc.)

### **2. Setup**

```bash
# Navigate to Frenly AI directory
cd /Users/Arief/Desktop/Nexus/frenly_ai

# Copy environment configuration
cp .env.example .env

# Edit .env with your API keys and settings
nano .env

# Install dependencies
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

### **3. Start Services**

```bash
# Development mode
docker-compose up --build

# Production mode
docker-compose -f docker-compose.production.yml up -d
```

### **4. Verify Installation**

- Backend: http://localhost:8765/health
- Frontend: http://localhost:3001
- Monitoring: http://localhost:3000 (Grafana)

---

## 🔧 **NEXUS PLATFORM INTEGRATION**

### **Frontend Integration**

#### **1. Add Avatar to Existing Pages**

```javascript
// In your main layout component
import FrenlyAvatar from "./frenly_ai/nexus_frontend/components/FrenlyAvatar";

const MainLayout = () => {
  const [frenlyMood, setFrenlyMood] = useState("idle");
  const [frenlyActive, setFrenlyActive] = useState(false);

  return (
    <div className="main-layout">
      {/* Your existing content */}
      <FrenlyAvatar
        mood={frenlyMood}
        isActive={frenlyActive}
        onAvatarClick={() => setFrenlyActive(!frenlyActive)}
        customImagePath="/IMG_E948BB7DF6B1-1.jpeg"
      />
    </div>
  );
};
```

#### **2. Conditional Injection**

```javascript
// frenly_injector.js
class FrenlyInjector {
  constructor() {
    this.excludedPages = ["/login", "/landing", "/error"];
    this.customImagePath = "/IMG_E948BB7DF6B1-1.jpeg";
  }

  shouldInject() {
    const currentPath = window.location.pathname;
    return !this.excludedPages.some((page) => currentPath.includes(page));
  }

  inject() {
    if (!this.shouldInject()) return;

    // Create avatar container
    const container = document.createElement("div");
    container.id = "frenly-ai-container";
    container.style.cssText = `
      position: fixed;
      top: 1rem;
      right: 1rem;
      z-index: 9999;
      pointer-events: none;
    `;
    document.body.appendChild(container);

    // Initialize React component
    const root = ReactDOM.createRoot(container);
    root.render(
      <FrenlyAvatar
        mood="idle"
        isActive={false}
        onAvatarClick={this.handleAvatarClick}
        customImagePath={this.customImagePath}
      />,
    );
  }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  new FrenlyInjector().inject();
});
```

### **Backend Integration**

#### **1. Add to Existing Backend**

```python
# In your main.py or app.py
from frenly_ai.backend.frenly_meta_agent import FrenlyMetaAgent

# Initialize Frenly AI
frenly_agent = FrenlyMetaAgent()

# Add WebSocket endpoint
@app.websocket("/frenly-ws")
async def frenly_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            context = json.loads(data)
            insight = await frenly_agent.generate_maximized_insight(context)
            await websocket.send_text(json.dumps(insight))
    except WebSocketDisconnect:
        pass
```

#### **2. API Integration**

```python
# Add Frenly AI endpoints to your existing API
@app.get("/api/frenly/status")
async def frenly_status():
    return await frenly_agent.get_system_status()

@app.post("/api/frenly/insight")
async def frenly_insight(context: dict):
    return await frenly_agent.generate_maximized_insight(context)
```

---

## 🎨 **CUSTOMIZATION**

### **Avatar Customization**

#### **1. Image Configuration**

```javascript
// AvatarConfig.js
export const AvatarConfig = {
  customImagePath: "/IMG_E948BB7DF6B1-1.jpeg",
  fallbackEnabled: true,
  size: { width: "60px", height: "60px" },
  border: { width: "3px", color: "#4CAF50", style: "solid" },
  shadow: { color: "rgba(0,0,0,0.15)", blur: "12px" },
};
```

#### **2. Mood Expressions**

```javascript
const moodExpressions = {
  idle: "😊",
  concerned: "😟",
  cheerful: "😄",
  serious: "🤔",
  excited: "🎉",
  thinking: "💭",
};
```

#### **3. Animation Customization**

```css
/* Custom animations in FrenlyAvatar.css */
.custom-animation {
  animation: customBounce 2s ease-in-out infinite;
}

@keyframes customBounce {
  0%,
  100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}
```

### **Plugin Development**

#### **1. Create Custom Plugin**

```python
# nexus_backend/plugins/custom_plugin.py
class CustomPlugin:
    def __init__(self):
        self.name = "CustomPlugin"
        self.priority = "medium"

    def is_relevant(self, context):
        return context.get('type') == 'custom_page'

    async def run(self, context):
        return {
            "type": "custom_insight",
            "message": "Custom insight generated!",
            "severity": "info",
            "data": {"custom": "data"}
        }
```

#### **2. Register Plugin**

```python
# In frenly_meta_agent.py
from plugins.custom_plugin import CustomPlugin

# Register plugin
plugin_manager.register_plugin(CustomPlugin())
```

---

## 🔍 **TROUBLESHOOTING**

### **Common Issues**

#### **1. Avatar Image Not Loading**

```bash
# Check if image exists
ls -la /Users/Arief/Desktop/Nexus/frenly_ai/nexus_frontend/public/IMG_E948BB7DF6B1-1.jpeg

# Verify image path in config
grep -r "IMG_E948BB7DF6B1-1.jpeg" nexus_frontend/
```

#### **2. WebSocket Connection Failed**

```bash
# Check backend service
curl http://localhost:8765/health

# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" http://localhost:8765/frenly-ws
```

#### **3. Plugin Loading Errors**

```bash
# Check plugin files
ls -la nexus_backend/plugins/

# Check plugin registration
grep -r "register_plugin" nexus_backend/
```

### **Debug Mode**

```bash
# Enable debug logging
export FRENLY_DEBUG=true
export LOG_LEVEL=debug

# Start with debug output
python nexus_backend/frenly_meta_agent.py --debug
```

---

## 📊 **MONITORING**

### **Health Checks**

- **Backend**: `GET /health`
- **Frontend**: Check browser console
- **WebSocket**: Connection status in browser dev tools
- **Plugins**: Plugin status in backend logs

### **Metrics**

- **Insight Generation Rate**: Insights per minute
- **User Engagement**: Click-through rates
- **System Performance**: Response times
- **Error Rates**: Failed requests and exceptions

---

## 🚀 **PRODUCTION DEPLOYMENT**

### **1. Environment Setup**

```bash
# Production environment variables
export ENVIRONMENT=production
export LOG_LEVEL=info
export FRENLY_DEBUG=false
export LLM_API_KEY=your_production_key
```

### **2. Docker Production Build**

```bash
# Build production images
docker-compose -f docker-compose.production.yml build

# Deploy with monitoring
docker-compose -f docker-compose.production.yml -f docker-compose.monitoring.yml up -d
```

### **3. Kubernetes Deployment**

```bash
# Apply Kubernetes manifests
kubectl apply -f kubernetes/

# Check deployment status
kubectl get pods -l app=frenly-ai
```

---

## 📚 **API REFERENCE**

### **WebSocket Messages**

```javascript
// Send context to Frenly AI
const message = {
  page: window.location.pathname,
  type: "dashboard",
  userRole: "management",
  timestamp: new Date().toISOString(),
};

websocket.send(JSON.stringify(message));
```

### **REST Endpoints**

- `GET /health` - System health check
- `GET /status` - Frenly AI status
- `POST /insight` - Generate insights
- `GET /plugins` - List available plugins

---

## 🎯 **NEXT STEPS**

1. **Deploy Backend Services**: Start with core AI engine
2. **Integrate Frontend**: Add avatar to existing pages
3. **Configure Plugins**: Enable page-specific intelligence
4. **Setup Monitoring**: Implement observability stack
5. **User Training**: Provide guidance on new features

---

**Status**: ✅ **READY FOR INTEGRATION**
**Support**: Refer to troubleshooting section or create an issue in the project repository.
