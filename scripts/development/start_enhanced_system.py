#!/usr/bin/env python3
"""
Frenly AI Enhanced System Launcher
Starts the complete unified system with master prompt and sectional controls
"""

import asyncio
import logging
import os
import sys

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def setup_logging():
    """Setup comprehensive logging for the enhanced system"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create logs directory
    os.makedirs("logs", exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/frenly_enhanced_system.log"),
            logging.FileHandler("logs/master_prompt_activity.log"),
        ],
    )

    # Set specific loggers
    logging.getLogger("websockets").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


def print_system_banner():
    """Print the enhanced system banner"""
    print(
        """
    ╔══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                              ║
    ║  🧠 FRENLY AI ENHANCED SYSTEM 🤖                                            ║
    ║                                                                              ║
    ║  Unified Multi-Agent Collective with Master Prompt & Sectional Controls     ║
    ║  Dynamic Role Separation • Domain Awareness • Gemini CLI Integration        ║
    ║                                                                              ║
    ╚══════════════════════════════════════════════════════════════════════════════╝
    """
    )


def print_feature_sections():
    """Print available feature sections"""
    print(
        """
    🔧 AVAILABLE FEATURE SECTIONS:

    ✅ Structural Analysis      - Continuous project structure analysis
    ✅ Dynamic Collaboration   - Real-time agent collaboration
    ✅ Automation Proposals    - Automatic optimization suggestions
    ✅ Load Balancing         - Intelligent workload distribution
    ✅ Gemini CLI Integration - Terminal-based AI assistance
    ✅ Quality Control        - Automated quality assurance
    ✅ Self-Healing          - Automatic failure recovery
    ✅ Real-time Monitoring  - Live system status updates

    💡 Use sectional controls to enable/disable features as needed
    """
    )


def print_domain_separation():
    """Print domain separation information"""
    print(
        """
    🏗️ DOMAIN SEPARATION:

    🔧 Operating System Layer
       • System services, environment configs, daemons, dependencies
       • Focus: Infrastructure and environment management

    ⚙️ Maintenance Layer
       • Automation, monitoring, load balancing, health checks
       • Focus: Operational excellence and system reliability

    💻 Application Layer
       • Codebase, nexus_frontend/backend, APIs, UI/UX, business logic
       • Focus: Application functionality and user experience

    🤝 All layers work together while maintaining clear boundaries
    """
    )


async def main():
    """Main entry point for the Frenly AI Enhanced System"""
    print_system_banner()
    print_feature_sections()
    print_domain_separation()

    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("🚀 Starting Frenly AI Enhanced System")
    logger.info("📋 Enhanced System Components:")
    logger.info("   • Master Prompt System (Dynamic Role Separation)")
    logger.info("   • Sectional Control System (Feature Management)")
    logger.info("   • Domain Separation (OS/Maintenance/Application)")
    logger.info("   • Brain Orchestrator (Frenly AI)")
    logger.info(
        "   • 6 Specialized Agents (System/Maintenance/Frontend/Backend/UX/Quality)"
    )
    logger.info("   • Communication Hub (Real-time Coordination)")
    logger.info("   • WebSocket Server (Frontend Integration)")
    logger.info("   • Gemini CLI Integration (Terminal AI Backup)")

    # Create and start the enhanced system
    system = FrenlyEnhancedSystem()

    try:
        await system.start_enhanced_system()
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt")
        print("\n🛑 Shutting down Frenly AI Enhanced System...")
    except Exception as e:
        logger.error(f"💥 Enhanced system error: {e}")
        print(f"\n💥 Enhanced system error: {e}")
    finally:
        await system.shutdown()
        print("\n✅ Frenly AI Enhanced System shutdown complete")


if __name__ == "__main__":
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    # Run the enhanced system
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n💥 Fatal error: {e}")
        sys.exit(1)
