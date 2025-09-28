#!/usr/bin/env python3
"""
Frenly AI LLM Interface
Multi-model LLM integration with fallback support
"""

import asyncio
import json
import logging
import os

import aiohttp

logger = logging.getLogger(__name__)


class LiveLLM:
    """Live LLM integration with multiple model support"""

    def __init__(self):
        self.models = {
            "primary": {
                "name": "gpt-4",
                "provider": "openai",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "enabled": True,
            },
            "fallback": {
                "name": "gpt-3.5-turbo",
                "provider": "openai",
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "enabled": True,
            },
            "alternative": {
                "name": "claude-3-sonnet",
                "provider": "anthropic",
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "base_url": "https://api.anthropic.com/v1",
                "enabled": bool(os.getenv("ANTHROPIC_API_KEY")),
            },
        }

        self.session = None
        self.request_count = 0
        self.error_count = 0

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def _build_openai_prompt(
        self,
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        plugin_outputs: Dict[str, Any],
    ) -> str:
        """Build OpenAI-compatible prompt"""

        prompt = f"""You are Frenly AI, an intelligent comic character assistant for the NEXUS Platform.

CONTEXT:
- Page: {context.get('page', 'unknown')}
- User Role: {context.get('userRole', 'user')}
- Page Type: {context.get('type', 'unknown')}
- User Agent: {context.get('userAgent', 'unknown')}
- Timestamp: {context.get('timestamp', 'unknown')}

RAG DATA:
{json.dumps(rag_data, indent=2) if rag_data else 'No RAG data available'}

PLUGIN OUTPUTS:
{json.dumps(plugin_outputs, indent=2) if plugin_outputs else 'No plugin outputs available'}

INSTRUCTIONS:
1. Analyze the context and data provided
2. Generate insights relevant to the user's role
3. Provide actionable recommendations
4. Use a friendly, helpful tone
5. Focus on practical, implementable suggestions
6. Consider security, performance, and user experience

RESPONSE FORMAT:
Provide a JSON response with:
- insights: List of key insights
- recommendations: List of actionable recommendations
- severity: "low", "medium", "high", or "critical"
- confidence: 0.0 to 1.0
- reasoning: Brief explanation of your analysis

Remember: You are a helpful comic character assistant. Be friendly, insightful, and practical."""

        return prompt

    def _build_anthropic_prompt(
        self,
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        plugin_outputs: Dict[str, Any],
    ) -> str:
        """Build Anthropic-compatible prompt"""

        prompt = f"""You are Frenly AI, an intelligent comic character assistant for the NEXUS Platform.

CONTEXT:
- Page: {context.get('page', 'unknown')}
- User Role: {context.get('userRole', 'user')}
- Page Type: {context.get('type', 'unknown')}

RAG DATA:
{json.dumps(rag_data, indent=2) if rag_data else 'No RAG data available'}

PLUGIN OUTPUTS:
{json.dumps(plugin_outputs, indent=2) if plugin_outputs else 'No plugin outputs available'}

Please analyze this data and provide insights relevant to the user's role. Be helpful, practical, and friendly in your response."""

        return prompt

    async def query_llm(
        self,
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        plugin_outputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Query LLM with fallback support"""

        if not self.session:
            self.session = aiohttp.ClientSession()

        # Try primary model first
        try:
            result = await self._query_openai(
                self.models["primary"], context, rag_data, plugin_outputs
            )
            if result:
                self.request_count += 1
                return result
        except Exception as e:
            logger.warning(f"Primary model failed: {e}")
            self.error_count += 1

        # Try fallback model
        try:
            result = await self._query_openai(
                self.models["fallback"], context, rag_data, plugin_outputs
            )
            if result:
                self.request_count += 1
                return result
        except Exception as e:
            logger.warning(f"Fallback model failed: {e}")
            self.error_count += 1

        # Try alternative model if available
        if self.models["alternative"]["enabled"]:
            try:
                result = await self._query_anthropic(
                    self.models["alternative"], context, rag_data, plugin_outputs
                )
                if result:
                    self.request_count += 1
                    return result
            except Exception as e:
                logger.warning(f"Alternative model failed: {e}")
                self.error_count += 1

        # If all models fail, return fallback response
        logger.error("All LLM models failed, returning fallback response")
        return self._get_fallback_response(context, rag_data, plugin_outputs)

    async def _query_openai(
        self,
        model_config: Dict[str, Any],
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        plugin_outputs: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Query OpenAI API"""

        if not model_config["api_key"]:
            raise ValueError("OpenAI API key not configured")

        prompt = self._build_openai_prompt(context, rag_data, plugin_outputs)

        headers = {
            "Authorization": f"Bearer {model_config['api_key']}",
            "Content-Type": "application/json",
        }

        data = {
            "model": model_config["name"],
            "messages": [
                {
                    "role": "system",
                    "content": "You are Frenly AI, a helpful comic character assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1000,
            "temperature": 0.7,
        }

        async with self.session.post(
            f"{model_config['base_url']}/chat/completions",
            headers=headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status == 200:
                result = await response.json()
                content = result["choices"][0]["message"]["content"]

                # Try to parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If not JSON, wrap in standard format
                    return {
                        "insights": [content],
                        "recommendations": [],
                        "severity": "info",
                        "confidence": 0.8,
                        "reasoning": "LLM response parsed as text",
                    }
            else:
                error_text = await response.text()
                raise Exception(f"OpenAI API error {response.status}: {error_text}")

    async def _query_anthropic(
        self,
        model_config: Dict[str, Any],
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        plugin_outputs: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Query Anthropic API"""

        if not model_config["api_key"]:
            raise ValueError("Anthropic API key not configured")

        prompt = self._build_anthropic_prompt(context, rag_data, plugin_outputs)

        headers = {
            "x-api-key": model_config["api_key"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": model_config["name"],
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}],
        }

        async with self.session.post(
            f"{model_config['base_url']}/messages",
            headers=headers,
            json=data,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status == 200:
                result = await response.json()
                content = result["content"][0]["text"]

                # Try to parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If not JSON, wrap in standard format
                    return {
                        "insights": [content],
                        "recommendations": [],
                        "severity": "info",
                        "confidence": 0.8,
                        "reasoning": "Anthropic response parsed as text",
                    }
            else:
                error_text = await response.text()
                raise Exception(f"Anthropic API error {response.status}: {error_text}")

    def _get_fallback_response(
        self,
        context: Dict[str, Any],
        rag_data: Dict[str, Any],
        plugin_outputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Get fallback response when all LLMs fail"""

        page_type = context.get("type", "unknown")
        user_role = context.get("userRole", "user")

        # Generate basic insights based on context
        insights = []
        recommendations = []

        if page_type == "dashboard":
            insights.append("Dashboard is loading successfully")
            recommendations.append("Consider adding more interactive widgets")
        elif page_type == "forms":
            insights.append("Form validation is working correctly")
            recommendations.append("Implement real-time validation feedback")
        elif page_type == "tables":
            insights.append("Table data is displaying properly")
            recommendations.append("Add sorting and filtering capabilities")
        else:
            insights.append("Page is functioning normally")
            recommendations.append("Monitor for any performance issues")

        # Add role-specific insights
        if user_role == "management":
            insights.append("Management dashboard is accessible")
            recommendations.append("Review key performance indicators")
        elif user_role == "auditor":
            insights.append("Audit trail is being maintained")
            recommendations.append("Schedule regular compliance reviews")
        elif user_role == "legal":
            insights.append("Legal compliance features are active")
            recommendations.append("Review data retention policies")
        elif user_role == "developer":
            insights.append("Development tools are available")
            recommendations.append("Check for any technical debt")

        return {
            "insights": insights,
            "recommendations": recommendations,
            "severity": "info",
            "confidence": 0.6,
            "reasoning": "Fallback response generated without LLM",
            "fallback": True,
        }


if __name__ == "__main__":
    # Test LLM interface
    async def test_llm():
        async with LiveLLM() as llm:
            context = {
                "page": "/dashboard",
                "userRole": "management",
                "type": "dashboard",
            }

            result = await llm.query_llm(context, {}, {})
            print(json.dumps(result, indent=2))

    asyncio.run(test_llm())
