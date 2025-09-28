#!/usr/bin/env python3
"""
Frenly AI Enhanced System
Integrates master prompt, sectional controls, and multi-agent coordination
"""

import asyncio
import json
import logging
import signal
import sys
from datetime import datetime

# Import all components
from agents.builder_agent import BuilderAgent
from agents.frontend_agent import FrontendAgent
from websocket_server import FrenlyWebSocketServer

logger = logging.getLogger(__name__)


class FrenlyEnhancedSystem:
    """Enhanced Frenly AI system with master prompt and sectional controls"""

    def __init__(self):
        # Core systems
        self.master_prompt = FrenlyMasterPrompt()
        self.sectional_control = SectionalControlSystem()
        self.brain_orchestrator = FrenlyBrainOrchestrator()
        self.communication_hub = AgentCommunicationHub()
        self.websocket_server = FrenlyWebSocketServer()

        # Initialize agents with master prompt guidance
        self.agents = self._initialize_agents_with_roles()

        # System state
        self.running = False
        self.tasks = []
        self.system_health = "healthy"
        self.domain_awareness = self._initialize_domain_awareness()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def _initialize_agents_with_roles(self) -> Dict[str, Any]:
        """Initialize agents with master prompt role guidance"""
        agents = {}

        # Get role guidance from master prompt
        role_guidance = {
            AgentRole.SYSTEM: BuilderAgent(
                "system_001"
            ),  # Using Builder as System agent
            AgentRole.MAINTENANCE: BuilderAgent(
                "maintenance_001"
            ),  # Using Builder as Maintenance agent
            AgentRole.FRONTEND: FrontendAgent("frontend_001"),
            AgentRole.BACKEND: BuilderAgent(
                "backend_001"
            ),  # Using Builder as Backend agent
            AgentRole.UX: FrontendAgent("ux_001"),  # Using Frontend as UX agent
            AgentRole.QUALITY: BuilderAgent(
                "quality_001"
            ),  # Using Builder as Quality agent
        }

        # Apply master prompt guidance to each agent
        for role, agent in role_guidance.items():
            role_guide = self.master_prompt.get_agent_role_guide(role)
            agent.role_guidance = role_guide
            agent.domain_layer = role_guide.get("domain", "application")
            agent.collaboration_style = role_guide.get("collaboration_style", "general")

            agents[role.value] = agent

        return agents

    def _initialize_domain_awareness(self) -> Dict[str, Any]:
        """Initialize domain awareness for system separation"""
        return {
            "operating_system": {
                "active_agents": [],
                "current_tasks": [],
                "monitoring": True,
                "boundaries": self.master_prompt.domain_separation[
                    DomainLayer.OPERATING_SYSTEM
                ]["boundaries"],
            },
            "maintenance": {
                "active_agents": [],
                "current_tasks": [],
                "monitoring": True,
                "boundaries": self.master_prompt.domain_separation[
                    DomainLayer.MAINTENANCE
                ]["boundaries"],
            },
            "application": {
                "active_agents": [],
                "current_tasks": [],
                "monitoring": True,
                "boundaries": self.master_prompt.domain_separation[
                    DomainLayer.APPLICATION
                ]["boundaries"],
            },
        }

    async def start_enhanced_system(self):
        """Start the enhanced Frenly AI system"""
        logger.info("🚀 Starting Frenly AI Enhanced System")

        try:
            # Start communication hub
            hub_task = asyncio.create_task(self.communication_hub.start_hub())
            self.tasks.append(hub_task)

            # Wait for hub to start
            await asyncio.sleep(1)

            # Start agents with master prompt guidance
            for agent_name, agent in self.agents.items():
                agent_task = asyncio.create_task(agent.start())
                self.tasks.append(agent_task)
                logger.info(f"🤖 Started {agent_name} agent with master prompt guidance")

            # Start brain orchestrator
            brain_task = asyncio.create_task(
                self.brain_orchestrator.start_workflow_cycle()
            )
            self.tasks.append(brain_task)

            # Start WebSocket server
            websocket_task = asyncio.create_task(self.websocket_server.start_server())
            self.tasks.append(websocket_task)

            self.running = True
            logger.info("✅ Frenly AI Enhanced System started successfully")

            # Create demonstration tasks with domain awareness
            await self._create_domain_aware_tasks()

            # Start enhanced system loop
            await self._run_enhanced_system_loop()

        except Exception as e:
            logger.error(f"Error starting enhanced system: {e}")
            await self.shutdown()

    async def _create_domain_aware_tasks(self):
        """Create tasks with domain separation awareness"""
        logger.info("📝 Creating domain-aware demonstration tasks")

        # Operating System Layer tasks
        await self.brain_orchestrator.create_task(
            title="System Environment Setup",
            description="Configure system environment and dependencies for Frenly AI",
            priority=5,
            tags=["operating_system", "environment", "dependencies"],
            domain="operating_system",
        )

        # Maintenance Layer tasks
        await self.brain_orchestrator.create_task(
            title="Automation Pipeline Setup",
            description="Implement automated monitoring and recovery systems",
            priority=4,
            tags=["maintenance", "automation", "monitoring"],
            domain="maintenance",
        )

        # Application Layer tasks
        await self.brain_orchestrator.create_task(
            title="Frenly AI Avatar Implementation",
            description="Create comic character avatar with multi-role intelligence",
            priority=5,
            tags=["application", "frontend", "ui", "avatar"],
            domain="application",
        )

        await self.brain_orchestrator.create_task(
            title="API Integration",
            description="Integrate Frenly AI with existing NEXUS Platform APIs",
            priority=4,
            tags=["application", "backend", "api", "integration"],
            domain="application",
        )

        logger.info("✅ Domain-aware tasks created")

    async def _run_enhanced_system_loop(self):
        """Enhanced system loop with master prompt guidance"""
        while self.running:
            try:
                # Apply master prompt principles
                await self._apply_master_prompt_principles()

                # Monitor sectional controls
                await self._monitor_sectional_controls()

                # Maintain domain separation
                await self._maintain_domain_separation()

                # Monitor system health
                await self._monitor_enhanced_system_health()

                # Check for structural analysis opportunities
                if self.sectional_control.sectional_controls[
                    FeatureSection.STRUCTURAL_ANALYSIS
                ].enabled:
                    await self._perform_structural_analysis()

                # Check for collaboration opportunities
                if self.sectional_control.sectional_controls[
                    FeatureSection.DYNAMIC_COLLABORATION
                ].enabled:
                    await self._check_enhanced_collaboration_opportunities()

                # Update system status
                await self._update_enhanced_system_status()

                # Sleep for a bit
                await asyncio.sleep(10)

            except Exception as e:
                logger.error(f"Error in enhanced system loop: {e}")
                await asyncio.sleep(5)

    async def _apply_master_prompt_principles(self):
        """Apply master prompt working principles"""
        try:
            # Dynamic adaptation
            await self._adapt_to_current_state()

            # Collaborative behavior
            await self._ensure_collaborative_behavior()

            # Collective objective alignment
            await self._align_with_global_objective()

            # Propositional first approach
            await self._propose_before_implementing()

            # Domain separation maintenance
            await self._maintain_domain_separation()

            # Resilient operation
            await self._ensure_resilient_operation()

            # Expandable system
            await self._suggest_improvements()

        except Exception as e:
            logger.error(f"Error applying master prompt principles: {e}")

    async def _adapt_to_current_state(self):
        """Adapt actions to current system state"""
        # Analyze current project structure
        current_structure = await self._analyze_project_structure()

        # Adapt agent behaviors based on structure
        for agent_name, agent in self.agents.items():
            if hasattr(agent, "adapt_to_structure"):
                await agent.adapt_to_structure(current_structure)

    async def _ensure_collaborative_behavior(self):
        """Ensure agents share insights and assist each other"""
        # Check for agents that can help others
        for agent_name, agent in self.agents.items():
            if agent.status == "idle" and hasattr(agent, "offer_assistance"):
                await agent.offer_assistance()

    async def _align_with_global_objective(self):
        """Align all agents with global objective"""
        # Ensure all agents are working toward the same goal
        global_objective = (
            "Build and maintain the NEXUS Platform with Frenly AI integration"
        )

        for agent_name, agent in self.agents.items():
            if hasattr(agent, "align_with_objective"):
                await agent.align_with_objective(global_objective)

    async def _propose_before_implementing(self):
        """Propose, evaluate, and decide before implementing"""
        # Get current tasks that need proposals
        pending_tasks = [
            task
            for task in self.brain_orchestrator.tasks.values()
            if task.status.value == "pending"
        ]

        for task in pending_tasks:
            # Generate proposals for the task
            proposals = await self._generate_task_proposals(task)

            # Evaluate proposals
            best_proposal = await self._evaluate_proposals(proposals)

            # Implement the best proposal
            if best_proposal:
                await self._implement_proposal(task, best_proposal)

    async def _maintain_domain_separation(self):
        """Maintain clear domain boundaries"""
        # Ensure agents respect domain boundaries
        for agent_name, agent in self.agents.items():
            if hasattr(agent, "domain_layer"):
                domain = agent.domain_layer
                boundaries = self.domain_awareness[domain]["boundaries"]

                # Check if agent is respecting boundaries
                if hasattr(agent, "check_domain_compliance"):
                    await agent.check_domain_compliance(boundaries)

    async def _ensure_resilient_operation(self):
        """Detect stuck tasks and restart automatically"""
        # Check for stuck tasks
        stuck_tasks = [
            task
            for task in self.brain_orchestrator.tasks.values()
            if task.status.value == "stuck"
        ]

        for task in stuck_tasks:
            logger.warning(f"🔄 Restarting stuck task: {task.title}")
            task.status = task.status.__class__("in_progress")
            task.started_at = datetime.now()
            task.progress = 0.0

    async def _suggest_improvements(self):
        """Continuously suggest system improvements"""
        if self.sectional_control.sectional_controls[
            FeatureSection.AUTOMATION_PROPOSALS
        ].enabled:
            # Generate improvement suggestions
            suggestions = await self._generate_improvement_suggestions()

            for suggestion in suggestions:
                logger.info(f"💡 Improvement suggestion: {suggestion}")

    async def _monitor_sectional_controls(self):
        """Monitor sectional control system"""
        # Check if any sections need attention
        for section, control in self.sectional_control.sectional_controls.items():
            if not control.enabled and control.impact_level == "high":
                logger.warning(f"⚠️ High-impact section disabled: {section.value}")

    async def _perform_structural_analysis(self):
        """Perform structural analysis of the project"""
        # Analyze project structure
        structure = await self._analyze_project_structure()

        # Identify optimization opportunities
        optimizations = await self._identify_optimizations(structure)

        # Propose structural improvements
        for optimization in optimizations:
            logger.info(f"🔍 Structural optimization: {optimization}")

    async def _check_enhanced_collaboration_opportunities(self):
        """Check for enhanced collaboration opportunities"""
        # Find agents that can collaborate
        active_agents = [
            agent for agent in self.agents.values() if agent.status == "active"
        ]

        for i, agent1 in enumerate(active_agents):
            for agent2 in active_agents[i + 1 :]:
                if self._can_collaborate(agent1, agent2):
                    await self._initiate_collaboration(agent1, agent2)

    async def _monitor_enhanced_system_health(self):
        """Monitor enhanced system health"""
        # Check sectional control health
        sectional_health = self.sectional_control.get_system_overview()

        # Check domain separation health
        domain_health = await self._check_domain_health()

        # Check agent health
        agent_health = {name: agent.get_status() for name, agent in self.agents.items()}

        # Update overall system health
        if sectional_health["system_health"] == "healthy" and domain_health["healthy"]:
            self.system_health = "healthy"
        else:
            self.system_health = "degraded"

    async def _update_enhanced_system_status(self):
        """Update enhanced system status"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.system_health,
            "master_prompt_active": True,
            "sectional_controls": self.sectional_control.get_system_overview(),
            "domain_awareness": self.domain_awareness,
            "agents": {name: agent.get_status() for name, agent in self.agents.items()},
            "brain_orchestrator": self.brain_orchestrator.get_system_status(),
            "communication_hub": self.communication_hub.get_hub_status(),
        }

        # Log status every minute
        if datetime.now().second == 0:
            logger.info(f"📊 Enhanced System Status: {json.dumps(status, indent=2)}")

    # Helper methods
    async def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze current project structure"""
        # This would analyze the actual project structure
        return {
            "files": 1000,
            "directories": 50,
            "languages": ["python", "javascript", "typescript"],
            "frameworks": ["react", "fastapi", "docker"],
            "complexity": "medium",
        }

    async def _generate_task_proposals(self, task) -> List[Dict[str, Any]]:
        """Generate proposals for a task"""
        # This would generate multiple approaches for the task
        return [
            {"approach": "aggressive", "time": "fast", "risk": "high"},
            {"approach": "conservative", "time": "slow", "risk": "low"},
            {"approach": "balanced", "time": "medium", "risk": "medium"},
        ]

    async def _evaluate_proposals(
        self, proposals: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Evaluate and select the best proposal"""
        # Simple evaluation - select balanced approach
        for proposal in proposals:
            if proposal["approach"] == "balanced":
                return proposal
        return proposals[0] if proposals else None

    async def _implement_proposal(self, task, proposal: Dict[str, Any]):
        """Implement the selected proposal"""
        logger.info(
            f"🚀 Implementing {proposal['approach']} approach for task: {task.title}"
        )

    async def _generate_improvement_suggestions(self) -> List[str]:
        """Generate improvement suggestions"""
        return [
            "Consider implementing automated testing for frontend components",
            "Add performance monitoring for API endpoints",
            "Implement caching strategy for database queries",
            "Add security scanning to CI/CD pipeline",
        ]

    def _can_collaborate(self, agent1, agent2) -> bool:
        """Check if two agents can collaborate"""
        # Simple collaboration check
        return (
            agent1.status == "active"
            and agent2.status == "active"
            and agent1.collaboration_style != agent2.collaboration_style
        )

    async def _initiate_collaboration(self, agent1, agent2):
        """Initiate collaboration between two agents"""
        logger.info(
            f"🤝 Initiating collaboration between {agent1.agent_id} and {agent2.agent_id}"
        )

    async def _check_domain_health(self) -> Dict[str, Any]:
        """Check domain separation health"""
        return {
            "healthy": True,
            "operating_system": "healthy",
            "maintenance": "healthy",
            "application": "healthy",
        }

    async def _identify_optimizations(self, structure: Dict[str, Any]) -> List[str]:
        """Identify structural optimizations"""
        optimizations = []

        if structure["complexity"] == "high":
            optimizations.append("Consider breaking down large components")

        if structure["files"] > 500:
            optimizations.append("Consider modularizing file structure")

        return optimizations

    # Public API methods
    async def control_feature_section(
        self, section: str, action: str
    ) -> Dict[str, Any]:
        """Control a feature section"""
        try:
            section_enum = FeatureSection(section)
            action_enum = ControlAction(action)
            return await self.sectional_control.control_feature_section(
                section_enum, action_enum
            )
        except ValueError as e:
            return {"error": f"Invalid section or action: {e}"}

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "timestamp": datetime.now().isoformat(),
            "running": self.running,
            "system_health": self.system_health,
            "master_prompt": self.master_prompt.get_system_status(),
            "sectional_controls": self.sectional_control.get_system_overview(),
            "domain_awareness": self.domain_awareness,
            "agents": {name: agent.get_status() for name, agent in self.agents.items()},
            "brain_orchestrator": self.brain_orchestrator.get_system_status(),
            "communication_hub": self.communication_hub.get_hub_status(),
        }

    async def get_sectional_control_options(self) -> Dict[str, Any]:
        """Get sectional control options"""
        return self.sectional_control.get_sectional_control_options()

    async def shutdown(self):
        """Gracefully shutdown the enhanced system"""
        logger.info("🛑 Shutting down Frenly AI Enhanced System")

        self.running = False

        # Cancel all tasks
        for task in self.tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        logger.info("✅ Frenly AI Enhanced System shutdown complete")


async def main():
    """Main entry point for the enhanced system"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/frenly_enhanced_system.log"),
        ],
    )

    # Create and start the enhanced system
    system = FrenlyEnhancedSystem()

    try:
        await system.start_enhanced_system()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Enhanced system error: {e}")
    finally:
        await system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
