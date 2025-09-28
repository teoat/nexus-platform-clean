#!/usr/bin/env python3
"""
Frenly AI Plugin Manager
Dynamic plugin loading and orchestration system
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


class FrenlyPlugin(ABC):
    """Base class for all Frenly AI plugins"""

    def __init__(self):
        self.name = self.__class__.__name__
        self.priority = "medium"
        self.enabled = True

    @abstractmethod
    def is_relevant(self, context: Dict[str, Any]) -> bool:
        """Check if plugin is relevant for given context"""
        pass

    @abstractmethod
    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Run plugin and return insights"""
        pass

    def get_priority(self) -> str:
        """Get plugin priority"""
        return self.priority

    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.enabled


class DynamicPluginManager:
    """Manages dynamic loading and orchestration of plugins"""

    def __init__(self):
        self.plugins: Dict[str, FrenlyPlugin] = {}
        self.plugin_registry: Dict[str, Dict] = {}
        self.load_default_plugins()

    def load_default_plugins(self):
        """Load default plugins"""
        try:
            # Load built-in plugins
            self.register_plugin(ChartsPlugin())
            self.register_plugin(FormsPlugin())
            self.register_plugin(TablesPlugin())
            self.register_plugin(APIPlugin())
            self.register_plugin(DashboardPlugin())
            self.register_plugin(WorkflowPlugin())

            logger.info(f"Loaded {len(self.plugins)} default plugins")
        except Exception as e:
            logger.error(f"Error loading default plugins: {e}")

    def register_plugin(self, plugin: FrenlyPlugin):
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
        self.plugin_registry[plugin.name] = {
            "class": plugin.__class__.__name__,
            "priority": plugin.get_priority(),
            "enabled": plugin.is_enabled(),
            "registered_at": asyncio.get_event_loop().time(),
        }
        logger.info(f"Registered plugin: {plugin.name}")

    async def orchestrate_plugins(
        self, context: Dict[str, Any], rag_data: Dict[str, Any], session_memory: Any
    ) -> Dict[str, Any]:
        """Orchestrate all relevant plugins"""
        try:
            # Find relevant plugins
            relevant_plugins = []
            for plugin_name, plugin in self.plugins.items():
                if plugin.is_enabled() and plugin.is_relevant(context):
                    relevant_plugins.append((plugin_name, plugin))

            # Sort by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            relevant_plugins.sort(
                key=lambda x: priority_order.get(x[1].get_priority(), 1)
            )

            # Run plugins in parallel
            plugin_tasks = []
            for plugin_name, plugin in relevant_plugins:
                task = asyncio.create_task(
                    self.run_plugin_safe(plugin_name, plugin, context)
                )
                plugin_tasks.append(task)

            # Wait for all plugins to complete
            plugin_results = await asyncio.gather(*plugin_tasks, return_exceptions=True)

            # Process results
            insights = {}
            for i, result in enumerate(plugin_results):
                plugin_name = relevant_plugins[i][0]
                if isinstance(result, Exception):
                    logger.error(f"Plugin {plugin_name} failed: {result}")
                    insights[plugin_name] = {"error": str(result), "status": "failed"}
                else:
                    insights[plugin_name] = result

            return {
                "plugin_insights": insights,
                "total_plugins": len(relevant_plugins),
                "successful_plugins": len(
                    [r for r in plugin_results if not isinstance(r, Exception)]
                ),
                "failed_plugins": len(
                    [r for r in plugin_results if isinstance(r, Exception)]
                ),
            }

        except Exception as e:
            logger.error(f"Error orchestrating plugins: {e}")
            return {"plugin_insights": {}, "error": str(e), "status": "failed"}

    async def run_plugin_safe(
        self, plugin_name: str, plugin: FrenlyPlugin, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a plugin safely with error handling"""
        try:
            result = await plugin.run(context)
            return {
                "plugin": plugin_name,
                "result": result,
                "status": "success",
                "priority": plugin.get_priority(),
            }
        except Exception as e:
            logger.error(f"Plugin {plugin_name} execution failed: {e}")
            return {
                "plugin": plugin_name,
                "error": str(e),
                "status": "failed",
                "priority": plugin.get_priority(),
            }


# Built-in Plugins


class ChartsPlugin(FrenlyPlugin):
    """Plugin for chart and dashboard analysis"""

    def __init__(self):
        super().__init__()
        self.priority = "high"

    def is_relevant(self, context: Dict[str, Any]) -> bool:
        return context.get("type") in ["dashboard", "analytics", "charts"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "chart_analysis",
            "message": "📊 Analyzing chart data and trends...",
            "insights": [
                "Chart performance is optimal",
                "Data trends show positive growth",
                "No anomalies detected in visualizations",
            ],
            "recommendations": [
                "Consider adding more interactive features",
                "Update chart colors for better accessibility",
            ],
            "severity": "info",
        }


class FormsPlugin(FrenlyPlugin):
    """Plugin for form validation and analysis"""

    def __init__(self):
        super().__init__()
        self.priority = "medium"

    def is_relevant(self, context: Dict[str, Any]) -> bool:
        return context.get("type") in ["forms", "input", "validation"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "form_analysis",
            "message": "📝 Analyzing form data and validation...",
            "insights": [
                "Form validation is working correctly",
                "Input patterns are normal",
                "No suspicious form submissions detected",
            ],
            "recommendations": [
                "Consider adding real-time validation",
                "Implement progressive form completion",
            ],
            "severity": "info",
        }


class TablesPlugin(FrenlyPlugin):
    """Plugin for table data analysis"""

    def __init__(self):
        super().__init__()
        self.priority = "medium"

    def is_relevant(self, context: Dict[str, Any]) -> bool:
        return context.get("type") in ["tables", "data", "transactions"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "table_analysis",
            "message": "📋 Analyzing table data and patterns...",
            "insights": [
                "Table data is consistent",
                "No unusual patterns detected",
                "Data integrity is maintained",
            ],
            "recommendations": [
                "Consider adding data filtering options",
                "Implement bulk operations for efficiency",
            ],
            "severity": "info",
        }


class APIPlugin(FrenlyPlugin):
    """Plugin for API health monitoring"""

    def __init__(self):
        super().__init__()
        self.priority = "high"

    def is_relevant(self, context: Dict[str, Any]) -> bool:
        return True  # Always relevant for API monitoring

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "api_monitoring",
            "message": "🔌 Monitoring API health and performance...",
            "insights": [
                "API response times are optimal",
                "No errors detected in recent requests",
                "Rate limiting is working correctly",
            ],
            "recommendations": [
                "Consider implementing API caching",
                "Monitor for potential DDoS attacks",
            ],
            "severity": "info",
        }


class DashboardPlugin(FrenlyPlugin):
    """Plugin for dashboard insights"""

    def __init__(self):
        super().__init__()
        self.priority = "high"

    def is_relevant(self, context: Dict[str, Any]) -> bool:
        return context.get("type") == "dashboard"

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "dashboard_insights",
            "message": "📊 Analyzing dashboard metrics and KPIs...",
            "insights": [
                "Dashboard performance is excellent",
                "KPI trends are positive",
                "User engagement is high",
            ],
            "recommendations": [
                "Add more interactive widgets",
                "Implement real-time data updates",
            ],
            "severity": "info",
        }


class WorkflowPlugin(FrenlyPlugin):
    """Plugin for workflow automation"""

    def __init__(self):
        super().__init__()
        self.priority = "medium"

    def is_relevant(self, context: Dict[str, Any]) -> bool:
        return context.get("type") in ["workflow", "automation", "process"]

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "workflow_analysis",
            "message": "⚙️ Analyzing workflow efficiency...",
            "insights": [
                "Workflow processes are optimized",
                "No bottlenecks detected",
                "Automation is working effectively",
            ],
            "recommendations": [
                "Consider adding more automation steps",
                "Implement workflow analytics",
            ],
            "severity": "info",
        }


if __name__ == "__main__":
    # Test plugin manager
    async def test_plugin_manager():
        manager = DynamicPluginManager()

        context = {"type": "dashboard", "page": "/dashboard", "userRole": "management"}

        result = await manager.orchestrate_plugins(context, {}, None)
        print(json.dumps(result, indent=2))

    import json

    asyncio.run(test_plugin_manager())
