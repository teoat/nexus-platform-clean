#!/usr/bin/env python3
"""
NEXUS Platform - Advanced Features Demo Script
Demonstrates AI Orchestrator and Advanced Monitoring capabilities
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, Any

class NexusAdvancedDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, data: Dict[Any, Any] = None) -> Dict[Any, Any]:
        """Make HTTP request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(url, json=data) as response:
                    return await response.json()
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    return await response.json()
        except Exception as e:
            return {"error": str(e), "endpoint": endpoint}
    
    async def test_ai_orchestrator(self):
        """Test AI Orchestrator functionality"""
        print("🤖 Testing AI Orchestrator...")
        
        # Test AI status
        status = await self.make_request("GET", "/api/v1/ai/status")
        print(f"   AI Status: {status.get('status', 'unknown')}")
        print(f"   Agents: {status.get('agents_count', 0)}")
        print(f"   Running: {status.get('orchestrator_running', False)}")
        
        # Test AI agents
        agents = await self.make_request("GET", "/api/v1/ai/agents")
        print(f"   Available Agents: {list(agents.get('agents', {}).keys())}")
        
        # Test task submission
        task_data = {
            "agent_type": "performance_optimizer",
            "task_type": "optimize_bundle",
            "description": "Optimize frontend bundle size",
            "priority": "high",
            "data": {"target_size": "500KB"}
        }
        
        task_result = await self.make_request("POST", "/api/v1/ai/tasks", task_data)
        print(f"   Task Submitted: {task_result.get('success', False)}")
        print(f"   Task ID: {task_result.get('data', {}).get('task_id', 'N/A')}")
        
        # Test AI health
        health = await self.make_request("GET", "/api/v1/ai/health")
        print(f"   AI Health: {health.get('status', 'unknown')}")
        
        return True
    
    async def test_advanced_monitoring(self):
        """Test Advanced Monitoring functionality"""
        print("\n📊 Testing Advanced Monitoring...")
        
        # Test monitoring status
        status = await self.make_request("GET", "/api/v1/monitoring/status")
        print(f"   Monitoring Status: {status.get('status', 'unknown')}")
        print(f"   Health Score: {status.get('health_score', 0)}")
        print(f"   Active Alerts: {status.get('active_alerts', 0)}")
        print(f"   Metrics Collected: {status.get('metrics_collected', 0)}")
        
        # Test metrics
        metrics = await self.make_request("GET", "/api/v1/monitoring/metrics")
        print(f"   Available Metrics: {len(metrics.get('metrics', []))}")
        for metric in metrics.get('metrics', [])[:3]:  # Show first 3
            print(f"     - {metric.get('name', 'unknown')}: {metric.get('value', 0)}{metric.get('unit', '')}")
        
        # Test alerts
        alerts = await self.make_request("GET", "/api/v1/monitoring/alerts")
        print(f"   Total Alerts: {alerts.get('total', 0)}")
        print(f"   Active Alerts: {alerts.get('active', 0)}")
        
        # Test predictions
        predictions = await self.make_request("GET", "/api/v1/monitoring/predictions")
        print(f"   Predictions Available: {len(predictions.get('predictions', []))}")
        for pred in predictions.get('predictions', []):
            print(f"     - {pred.get('metric_name', 'unknown')}: {pred.get('predicted_value', 0)} (confidence: {pred.get('confidence', 0)})")
        
        # Test dashboard
        dashboard = await self.make_request("GET", "/api/v1/monitoring/dashboard")
        print(f"   Dashboard Health: {dashboard.get('system_health', 0)}")
        print(f"   Monitoring Status: {dashboard.get('monitoring_status', 'unknown')}")
        
        return True
    
    async def test_ssot_system(self):
        """Test SSOT system functionality"""
        print("\n🔗 Testing SSOT System...")
        
        # Test SSOT status
        aliases = await self.make_request("GET", "/api/v1/ssot/aliases")
        print(f"   SSOT Aliases: {aliases.get('total', 0)}")
        
        # Create a test alias
        alias_data = {
            "name": "demo-service",
            "canonical": "api-demo-service",
            "context": "frontend",
            "description": "Demo service for testing"
        }
        
        create_result = await self.make_request("POST", "/api/v1/ssot/aliases", alias_data)
        print(f"   Alias Created: {create_result.get('success', False)}")
        
        # Resolve the alias
        resolve_result = await self.make_request("GET", f"/api/v1/ssot/resolve/demo-service?context=frontend")
        print(f"   Alias Resolved: {resolve_result.get('canonical', 'N/A')}")
        
        return True
    
    async def test_system_health(self):
        """Test overall system health"""
        print("\n🏥 Testing System Health...")
        
        # Test backend health
        health = await self.make_request("GET", "/health")
        print(f"   Backend Health: {health.get('status', 'unknown')}")
        
        # Test system status
        status = await self.make_request("GET", "/api/status")
        print(f"   System Status: {status.get('status', 'unknown')}")
        print(f"   Services: {status.get('services', {})}")
        
        return True
    
    async def run_comprehensive_demo(self):
        """Run comprehensive demo of all features"""
        print("🚀 NEXUS Platform - Advanced Features Demo")
        print("=" * 50)
        
        start_time = time.time()
        
        try:
            # Test all components
            await self.test_system_health()
            await self.test_ssot_system()
            await self.test_ai_orchestrator()
            await self.test_advanced_monitoring()
            
            end_time = time.time()
            duration = end_time - start_time
            
            print("\n" + "=" * 50)
            print("✅ Demo completed successfully!")
            print(f"⏱️  Total time: {duration:.2f} seconds")
            print(f"🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
            return False
        
        return True

async def main():
    """Main demo function"""
    async with NexusAdvancedDemo() as demo:
        success = await demo.run_comprehensive_demo()
        return success

if __name__ == "__main__":
    print("Starting NEXUS Advanced Features Demo...")
    success = asyncio.run(main())
    exit(0 if success else 1)
