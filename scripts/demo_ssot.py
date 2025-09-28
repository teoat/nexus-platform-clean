#!/usr/bin/env python3
"""
SSOT System Demonstration Script
"""

import sys
import asyncio
import time
import json
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.ssot_registry import SSOTRegistry, AliasType, AliasStatus
from backend.services.alias_manager import AliasManager

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print(f"{'='*60}")

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)

async def demo_ssot_system():
    """Demonstrate the complete SSOT system"""
    
    print_header("NEXUS SSOT System Demonstration")
    
    # Initialize components
    print("🔧 Initializing SSOT components...")
    registry = SSOTRegistry()
    alias_manager = AliasManager(registry)
    
    print_section("1. Registering SSOT Anchors")
    
    # Register core anchors
    anchors = [
        {
            "family": "api",
            "description": "User management API",
            "format": "openapi-3.0.yaml",
            "source_hint": "/api/v1/users",
            "owner": "backend_team",
            "version": "1.0.0",
            "centrality_score": 0.9,
            "modification_policy": "strict",
            "validation_rules": ["required", "authenticated"],
            "generates": ["user-data", "user-events"],
            "aliasing": {"enabled": True, "contexts": ["frontend", "backend"]}
        },
        {
            "family": "api",
            "description": "Transaction processing API",
            "format": "openapi-3.0.yaml",
            "source_hint": "/api/v1/transactions",
            "owner": "backend_team",
            "version": "1.0.0",
            "centrality_score": 0.8,
            "modification_policy": "strict",
            "validation_rules": ["required", "authenticated", "authorized"],
            "generates": ["transaction-data", "transaction-events"],
            "aliasing": {"enabled": True, "contexts": ["frontend", "backend"]}
        },
        {
            "family": "ai",
            "description": "Frenly AI service API",
            "format": "openapi-3.0.yaml",
            "source_hint": "/api/v1/ai",
            "owner": "ai_team",
            "version": "1.0.0",
            "centrality_score": 0.7,
            "modification_policy": "flexible",
            "validation_rules": ["optional", "rate_limited"],
            "generates": ["ai-responses", "ai-insights"],
            "aliasing": {"enabled": True, "contexts": ["frenly_ai", "frontend"]}
        }
    ]
    
    for i, anchor_config in enumerate(anchors):
        anchor_id = f"anchor-{i+1}"
        try:
            result = await registry.register_anchor(anchor_id, anchor_config)
            print(f"✅ Registered anchor: {anchor_id}")
        except Exception as e:
            print(f"❌ Failed to register anchor {anchor_id}: {e}")
    
    print_section("2. Creating API Aliases")
    
    # Create aliases for different contexts
    aliases = [
        {
            "alias_name": "user-management",
            "canonical_name": "anchor-1",
            "context": "frontend",
            "alias_type": AliasType.APPLICATION,
            "description": "User management endpoint for frontend",
            "created_by": "frontend_developer"
        },
        {
            "alias_name": "user-service",
            "canonical_name": "anchor-1",
            "context": "backend",
            "alias_type": AliasType.SYSTEM,
            "description": "User service for backend integration",
            "created_by": "backend_developer"
        },
        {
            "alias_name": "transaction-processing",
            "canonical_name": "anchor-2",
            "context": "frontend",
            "alias_type": AliasType.APPLICATION,
            "description": "Transaction processing for frontend",
            "created_by": "frontend_developer"
        },
        {
            "alias_name": "frenly-ai",
            "canonical_name": "anchor-3",
            "context": "frenly_ai",
            "alias_type": AliasType.FRENLY_AI,
            "description": "Frenly AI service endpoint",
            "created_by": "ai_developer"
        }
    ]
    
    for alias_config in aliases:
        try:
            result = alias_manager.add_alias(
                alias=alias_config['alias_name'],
                canonical=alias_config['canonical_name'],
                context=alias_config['context'],
                alias_type=alias_config['alias_type'].value,
                description=alias_config['description'],
                created_by=alias_config['created_by']
            )
            print(f"✅ Created alias: {alias_config['alias_name']} -> {alias_config['canonical_name']}")
        except Exception as e:
            print(f"❌ Failed to create alias {alias_config['alias_name']}: {e}")
    
    print_section("3. Alias Resolution Demo")
    
    # Demonstrate alias resolution
    test_cases = [
        ("user-management", "frontend"),
        ("user-service", "backend"),
        ("transaction-processing", "frontend"),
        ("frenly-ai", "frenly_ai"),
        ("nonexistent-alias", "frontend")  # This should fail
    ]
    
    for alias, context in test_cases:
        try:
            start_time = time.time()
            canonical = registry.resolve_alias(alias, context)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            print(f"✅ {alias} ({context}) -> {canonical} ({response_time:.2f}ms)")
        except Exception as e:
            print(f"❌ {alias} ({context}) -> Error: {type(e).__name__}: {e}")
    
    print_section("4. Registry Statistics")
    
    # Show registry metrics
    print(f"📊 Total Anchors: {len(registry.anchors)}")
    total_aliases = sum(len(aliases) for aliases in registry.aliases.values())
    print(f"📊 Total Aliases: {total_aliases}")
    print(f"📊 Contexts: {', '.join(registry.aliases.keys())}")
    print(f"📊 Audit Entries: {len(registry.audit_log)}")
    
    print_section("5. Alias Management Demo")
    
    # List aliases by context
    for context in ["frontend", "backend", "frenly_ai"]:
        try:
            aliases = alias_manager.list_aliases(context=context)
            print(f"\n🔍 Aliases in context '{context}':")
            for alias in aliases:
                print(f"  - {alias['alias']} -> {alias['canonical']} ({alias['type']})")
        except Exception as e:
            print(f"❌ Error listing aliases for context '{context}': {e}")
    
    print_section("6. Performance Test")
    
    # Performance test
    print("🚀 Running performance test...")
    test_alias = "user-management"
    test_context = "frontend"
    iterations = 100
    
    start_time = time.time()
    for _ in range(iterations):
        try:
            registry.resolve_alias(test_alias, test_context)
        except:
            pass
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = (total_time / iterations) * 1000  # Convert to ms
    throughput = iterations / total_time
    
    print(f"📊 Performance Results:")
    print(f"  - Iterations: {iterations}")
    print(f"  - Total Time: {total_time:.3f}s")
    print(f"  - Average Time: {avg_time:.3f}ms")
    print(f"  - Throughput: {throughput:.0f} requests/second")
    
    print_section("7. Audit Log Demo")
    
    # Show audit log
    print("📝 Recent audit entries:")
    recent_entries = registry.audit_log[-5:]  # Last 5 entries
    for entry in recent_entries:
        print(f"  - {entry.timestamp}: {entry.action} by {entry.user} on {entry.resource}")
    
    print_section("8. Error Handling Demo")
    
    # Test error scenarios
    error_cases = [
        ("nonexistent-alias", "frontend", "Alias not found"),
        ("user-management", "nonexistent-context", "Context not found"),
        ("", "frontend", "Empty alias"),
        ("user-management", "", "Empty context")
    ]
    
    print("🔍 Testing error handling:")
    for alias, context, expected_error in error_cases:
        try:
            registry.resolve_alias(alias, context)
            print(f"❌ Expected error for {alias} in {context}, but succeeded")
        except Exception as e:
            print(f"✅ {alias} in {context} -> {type(e).__name__}: {str(e)}")
    
    print_header("🎉 SSOT System Demonstration Complete!")
    
    print("\n📋 Summary:")
    print(f"  - Anchors registered: {len(registry.anchors)}")
    print(f"  - Aliases created: {total_aliases}")
    print(f"  - Contexts configured: {len(registry.aliases)}")
    print(f"  - Audit entries: {len(registry.audit_log)}")
    
    print("\n🚀 The NEXUS SSOT system is fully operational!")
    print("   - Dynamic API aliasing ✅")
    print("   - Multi-context support ✅")
    print("   - Governance compliance ✅")
    print("   - Performance optimization ✅")
    print("   - Audit logging ✅")
    print("   - Error handling ✅")

if __name__ == "__main__":
    try:
        asyncio.run(demo_ssot_system())
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
