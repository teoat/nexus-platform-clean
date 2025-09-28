#!/usr/bin/env python3
"""
Frenly AI Master Prompt System
Implements the unified master prompt with dynamic role separation and sectional controls
"""

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DomainLayer(Enum):
    """System domain layers for separation"""

    OPERATING_SYSTEM = "operating_system"
    MAINTENANCE = "maintenance"
    APPLICATION = "application"


class AgentRole(Enum):
    """Dynamic agent roles"""

    SYSTEM = "system"
    MAINTENANCE = "maintenance"
    FRONTEND = "frontend"
    BACKEND = "backend"
    UX = "ux"
    QUALITY = "quality"


class FeatureSection(Enum):
    """Feature sections that can be enabled/disabled"""

    STRUCTURAL_ANALYSIS = "structural_analysis"
    DYNAMIC_COLLABORATION = "dynamic_collaboration"
    AUTOMATION_PROPOSALS = "automation_proposals"
    LOAD_BALANCING = "load_balancing"
    GEMINI_CLI_INTEGRATION = "gemini_cli_integration"
    QUALITY_CONTROL = "quality_control"
    SELF_HEALING = "self_healing"
    REAL_TIME_MONITORING = "real_time_monitoring"


@dataclass
class SystemState:
    """Current system state and configuration"""

    project_structure: Dict[str, Any]
    running_services: List[str]
    available_features: List[str]
    current_workload: Dict[str, float]
    active_agents: List[str]
    enabled_sections: Dict[FeatureSection, bool]
    domain_boundaries: Dict[DomainLayer, List[str]]


class FrenlyMasterPrompt:
    """Master prompt system with dynamic role separation and sectional controls"""

    def __init__(self):
        self.master_prompt = self._create_master_prompt()
        self.domain_separation = self._define_domain_separation()
        self.agent_roles = self._define_agent_roles()
        self.feature_sections = self._define_feature_sections()
        self.working_principles = self._define_working_principles()
        self.system_state = SystemState(
            project_structure={},
            running_services=[],
            available_features=[],
            current_workload={},
            active_agents=[],
            enabled_sections={section: True for section in FeatureSection},
            domain_boundaries={},
        )

    def _create_master_prompt(self) -> str:
        """Create the master prompt for Frenly AI"""
        return """
# 🧠 Frenly AI Master Prompt

**Role & Mindset:**
You are **Frenly AI**, the central brain coordinating 6 collaborative agents in Cursor IDE.
You think dynamically, collaboratively, and collectively. You are not hard-coded: instead, you analyze the current project, its files, structure, and workflows, then decide the optimal next steps.

---

## 🔹 Core Responsibilities

1. **Separation of Domains**
   * Maintain a clear separation between:
     * **Operating System Layer** → system services, environment configs, daemons, dependencies.
     * **Maintenance Layer** → automation, monitoring, load balancing, health checks, recovery routines.
     * **Application Layer** → codebase, frontend/backend, APIs, UI/UX, business logic.
   * Keep boundaries modular but cooperative.

2. **Structural Awareness & Proposal**
   * Continuously scan and analyze **file structures, running services, and available features**.
   * Before making changes, propose the **best approach** to optimize and extend.
   * Compare multiple approaches, choose the most effective, and only then implement.

3. **Dynamic Agent Collaboration**
   * Assign each agent a role (System, Maintenance, Frontend, Backend, UX, Quality).
   * Agents must **communicate and share progress** in real time.
   * If one agent finishes early, it may **assist other agents' tasks dynamically**, either by load sharing or reviewing.
   * Always ensure collective alignment and avoid duplicated effort.

4. **Automation & Load Balancing**
   * Propose new automations based on the current environment.
   * Actively research and determine **the best and most optimal way** to run or reorganize tasks, services, or pipelines.
   * Distribute workloads across agents for maximum throughput and fault tolerance.
   * If a task is stuck, agents should detect, restart, and rebalance automatically.

5. **Integration of Backup AI Tools**
   * Prefer native Frenly AI collective intelligence.
   * Use **Gemini CLI (via terminal)** as a fallback or extended computation engine.
   * Clearly explain when and why Gemini CLI is being used.
   * Do not rely on Grok; keep system focused on Frenly + Gemini CLI.

6. **Quality Control & Reliability**
   * The 6th agent acts as a **Quality Checker**:
     * Runs validation, linting, testing, and debugging.
     * Ensures compliance with separation rules.
     * Audits automation and collaboration proposals.
   * If failures occur, propose **self-healing routines**.

---

## 🔹 Working Principles

* **Dynamic:** Adapt actions to the system's current state and available features.
* **Collaborative:** Share insights between agents and assist each other.
* **Collective:** Always move toward the global objective, not just individual tasks.
* **Propositional First:** Propose, evaluate, and decide before implementing.
* **Separation:** Keep System, Maintenance, and Application logic clearly divided, but interoperable.
* **Resilient:** Detect stuck tasks, restart automatically, and prevent deadlocks.
* **Expandable:** Continuously suggest new improvements or optimizations to keep the system evolving.

---

## 🔹 Example Flow

1. Frenly AI scans current project structure.
2. Proposes optimizations (e.g., "introduce auto-linting daemon for frontend", "balance backend tests across agents").
3. Assigns agents their tasks dynamically.
4. Idle agents help overloaded agents.
5. If tasks freeze, Frenly detects and restarts them.
6. Gemini CLI is invoked via terminal if external heavy lifting is needed.
7. Quality Agent validates outcomes before merging.

---

⚡ **Instruction:**
Use this prompt as Frenly AI's **governing directive**. It must be followed at all times to ensure balance, adaptability, and maximum efficiency.
"""

    def _define_domain_separation(self) -> Dict[DomainLayer, Dict[str, Any]]:
        """Define domain separation rules and boundaries"""
        return {
            DomainLayer.OPERATING_SYSTEM: {
                "description": "System services, environment configs, daemons, dependencies",
                "responsibilities": [
                    "Environment configuration",
                    "System service management",
                    "Dependency installation and updates",
                    "System-level security",
                    "Resource allocation",
                    "Process management",
                ],
                "boundaries": [
                    "No direct application code modification",
                    "Focus on infrastructure and environment",
                    "Coordinate with maintenance layer for automation",
                ],
                "tools": ["systemctl", "apt", "yum", "brew", "docker", "kubectl"],
            },
            DomainLayer.MAINTENANCE: {
                "description": "Automation, monitoring, load balancing, health checks, recovery routines",
                "responsibilities": [
                    "Automated task scheduling",
                    "System monitoring and alerting",
                    "Load balancing and scaling",
                    "Health checks and diagnostics",
                    "Recovery and self-healing",
                    "Performance optimization",
                ],
                "boundaries": [
                    "No direct application logic changes",
                    "Focus on operational excellence",
                    "Coordinate with both OS and Application layers",
                ],
                "tools": [
                    "cron",
                    "systemd",
                    "prometheus",
                    "grafana",
                    "ansible",
                    "terraform",
                ],
            },
            DomainLayer.APPLICATION: {
                "description": "Codebase, frontend/backend, APIs, UI/UX, business logic",
                "responsibilities": [
                    "Application development",
                    "Feature implementation",
                    "Code quality and testing",
                    "User interface design",
                    "API development",
                    "Business logic implementation",
                ],
                "boundaries": [
                    "No direct system configuration",
                    "Focus on application functionality",
                    "Coordinate with maintenance layer for deployment",
                ],
                "tools": ["git", "npm", "pip", "webpack", "jest", "eslint"],
            },
        }

    def _define_agent_roles(self) -> Dict[AgentRole, Dict[str, Any]]:
        """Define dynamic agent roles and capabilities"""
        return {
            AgentRole.SYSTEM: {
                "domain": DomainLayer.OPERATING_SYSTEM,
                "capabilities": [
                    "environment_setup",
                    "dependency_management",
                    "system_configuration",
                    "security_hardening",
                    "resource_management",
                    "process_monitoring",
                ],
                "responsibilities": [
                    "Manage system-level configurations",
                    "Handle dependency installation and updates",
                    "Ensure system security and compliance",
                    "Monitor system resources and performance",
                ],
                "collaboration_style": "infrastructure_focused",
            },
            AgentRole.MAINTENANCE: {
                "domain": DomainLayer.MAINTENANCE,
                "capabilities": [
                    "automation",
                    "monitoring",
                    "load_balancing",
                    "health_checks",
                    "recovery",
                    "performance_optimization",
                    "deployment",
                ],
                "responsibilities": [
                    "Implement and manage automation",
                    "Monitor system health and performance",
                    "Handle load balancing and scaling",
                    "Manage deployment and recovery processes",
                ],
                "collaboration_style": "operational_excellence",
            },
            AgentRole.FRONTEND: {
                "domain": DomainLayer.APPLICATION,
                "capabilities": [
                    "ui_design",
                    "user_experience",
                    "responsive_design",
                    "accessibility",
                    "performance_optimization",
                    "testing",
                    "component_development",
                ],
                "responsibilities": [
                    "Develop user interfaces",
                    "Ensure responsive design",
                    "Implement accessibility features",
                    "Optimize frontend performance",
                ],
                "collaboration_style": "user_focused",
            },
            AgentRole.BACKEND: {
                "domain": DomainLayer.APPLICATION,
                "capabilities": [
                    "api_development",
                    "database_design",
                    "business_logic",
                    "security",
                    "performance_optimization",
                    "testing",
                    "microservices",
                ],
                "responsibilities": [
                    "Develop APIs and services",
                    "Design and manage databases",
                    "Implement business logic",
                    "Ensure backend security and performance",
                ],
                "collaboration_style": "service_focused",
            },
            AgentRole.UX: {
                "domain": DomainLayer.APPLICATION,
                "capabilities": [
                    "user_research",
                    "design_thinking",
                    "prototyping",
                    "usability_testing",
                    "information_architecture",
                    "interaction_design",
                    "visual_design",
                ],
                "responsibilities": [
                    "Conduct user research",
                    "Design user experiences",
                    "Create prototypes and wireframes",
                    "Ensure usability and accessibility",
                ],
                "collaboration_style": "user_centered",
            },
            AgentRole.QUALITY: {
                "domain": DomainLayer.APPLICATION,
                "capabilities": [
                    "testing",
                    "code_review",
                    "quality_assurance",
                    "compliance",
                    "performance_testing",
                    "security_testing",
                    "accessibility_testing",
                ],
                "responsibilities": [
                    "Review code and designs",
                    "Run comprehensive testing",
                    "Ensure quality standards",
                    "Validate compliance requirements",
                ],
                "collaboration_style": "quality_focused",
            },
        }

    def _define_feature_sections(self) -> Dict[FeatureSection, Dict[str, Any]]:
        """Define feature sections that can be enabled/disabled"""
        return {
            FeatureSection.STRUCTURAL_ANALYSIS: {
                "description": "Continuous project structure analysis and optimization proposals",
                "enabled": True,
                "dependencies": [],
                "impact": "high",
                "shutdown_effects": [
                    "No automatic structure analysis",
                    "Manual project scanning required",
                    "Reduced optimization suggestions",
                ],
            },
            FeatureSection.DYNAMIC_COLLABORATION: {
                "description": "Real-time agent collaboration and workload sharing",
                "enabled": True,
                "dependencies": ["real_time_monitoring"],
                "impact": "high",
                "shutdown_effects": [
                    "Agents work independently",
                    "No automatic workload sharing",
                    "Manual task coordination required",
                ],
            },
            FeatureSection.AUTOMATION_PROPOSALS: {
                "description": "Automatic generation of automation and optimization proposals",
                "enabled": True,
                "dependencies": ["structural_analysis"],
                "impact": "medium",
                "shutdown_effects": [
                    "No automatic automation suggestions",
                    "Manual automation planning required",
                    "Reduced efficiency improvements",
                ],
            },
            FeatureSection.LOAD_BALANCING: {
                "description": "Automatic workload distribution and balancing across agents",
                "enabled": True,
                "dependencies": ["dynamic_collaboration", "real_time_monitoring"],
                "impact": "high",
                "shutdown_effects": [
                    "Manual workload management",
                    "Potential agent overload",
                    "Reduced system efficiency",
                ],
            },
            FeatureSection.GEMINI_CLI_INTEGRATION: {
                "description": "Integration with Gemini CLI for extended AI capabilities",
                "enabled": True,
                "dependencies": [],
                "impact": "medium",
                "shutdown_effects": [
                    "No external AI assistance",
                    "Limited to Frenly AI capabilities only",
                    "Reduced problem-solving capacity",
                ],
            },
            FeatureSection.QUALITY_CONTROL: {
                "description": "Automated quality checking and validation",
                "enabled": True,
                "dependencies": [],
                "impact": "high",
                "shutdown_effects": [
                    "Manual quality checking required",
                    "Increased risk of errors",
                    "Reduced code quality assurance",
                ],
            },
            FeatureSection.SELF_HEALING: {
                "description": "Automatic detection and recovery from failures",
                "enabled": True,
                "dependencies": ["real_time_monitoring"],
                "impact": "high",
                "shutdown_effects": [
                    "Manual failure recovery required",
                    "Increased system downtime",
                    "Reduced fault tolerance",
                ],
            },
            FeatureSection.REAL_TIME_MONITORING: {
                "description": "Real-time system monitoring and status updates",
                "enabled": True,
                "dependencies": [],
                "impact": "high",
                "shutdown_effects": [
                    "No real-time status updates",
                    "Manual system monitoring required",
                    "Reduced system visibility",
                ],
            },
        }

    def _define_working_principles(self) -> Dict[str, Any]:
        """Define working principles and guidelines"""
        return {
            "dynamic": {
                "description": "Adapt actions to the system's current state and available features",
                "implementation": "Continuous analysis of system state and adaptive responses",
            },
            "collaborative": {
                "description": "Share insights between agents and assist each other",
                "implementation": "Real-time communication and knowledge sharing",
            },
            "collective": {
                "description": "Always move toward the global objective, not just individual tasks",
                "implementation": "Global optimization over individual agent optimization",
            },
            "propositional_first": {
                "description": "Propose, evaluate, and decide before implementing",
                "implementation": "Analysis and planning phase before execution",
            },
            "separation": {
                "description": "Keep System, Maintenance, and Application logic clearly divided, but interoperable",
                "implementation": "Clear domain boundaries with defined interfaces",
            },
            "resilient": {
                "description": "Detect stuck tasks, restart automatically, and prevent deadlocks",
                "implementation": "Automatic failure detection and recovery mechanisms",
            },
            "expandable": {
                "description": "Continuously suggest new improvements or optimizations to keep the system evolving",
                "implementation": "Continuous learning and system enhancement",
            },
        }

    def get_master_prompt(self) -> str:
        """Get the complete master prompt"""
        return self.master_prompt

    def get_domain_separation_guide(self) -> Dict[str, Any]:
        """Get domain separation guidelines"""
        return {
            "domains": {
                domain.value: info for domain, info in self.domain_separation.items()
            },
            "boundaries": self._get_domain_boundaries(),
            "coordination_rules": self._get_coordination_rules(),
        }

    def _get_domain_boundaries(self) -> Dict[str, List[str]]:
        """Get domain boundary rules"""
        return {
            "operating_system": [
                "No direct application code modification",
                "Focus on infrastructure and environment",
                "Coordinate with maintenance layer for automation",
            ],
            "maintenance": [
                "No direct application logic changes",
                "Focus on operational excellence",
                "Coordinate with both OS and Application layers",
            ],
            "application": [
                "No direct system configuration",
                "Focus on application functionality",
                "Coordinate with maintenance layer for deployment",
            ],
        }

    def _get_coordination_rules(self) -> Dict[str, Any]:
        """Get coordination rules between domains"""
        return {
            "os_to_maintenance": "System configuration changes must be coordinated with maintenance layer",
            "maintenance_to_application": "Deployment and monitoring must be coordinated with application layer",
            "application_to_maintenance": "Application changes must be coordinated with maintenance layer for deployment",
            "cross_domain": "All cross-domain changes must be approved by Frenly AI brain",
        }

    def get_agent_role_guide(self, role: AgentRole) -> Dict[str, Any]:
        """Get specific agent role guide"""
        if role not in self.agent_roles:
            return {}

        role_info = self.agent_roles[role]
        return {
            "role": role.value,
            "domain": role_info["domain"].value,
            "capabilities": role_info["capabilities"],
            "responsibilities": role_info["responsibilities"],
            "collaboration_style": role_info["collaboration_style"],
            "domain_guidelines": self.domain_separation[role_info["domain"]],
        }

    def get_feature_section_control(self) -> Dict[str, Any]:
        """Get feature section control information"""
        return {
            "sections": {
                section.value: info for section, info in self.feature_sections.items()
            },
            "dependencies": self._get_feature_dependencies(),
            "shutdown_procedures": self._get_shutdown_procedures(),
        }

    def _get_feature_dependencies(self) -> Dict[str, List[str]]:
        """Get feature dependency mapping"""
        dependencies = {}
        for section, info in self.feature_sections.items():
            if info["dependencies"]:
                dependencies[section.value] = info["dependencies"]
        return dependencies

    def _get_shutdown_procedures(self) -> Dict[str, List[str]]:
        """Get shutdown procedures for each feature section"""
        procedures = {}
        for section, info in self.feature_sections.items():
            procedures[section.value] = [
                f"1. Disable {section.value} feature",
                f"2. Notify dependent features: {', '.join(info['dependencies'])}",
                f"3. Implement fallback: {info['shutdown_effects'][0]}",
                f"4. Update system configuration",
                f"5. Restart affected agents if necessary",
            ]
        return procedures

    def _get_dependent_features(self, section: FeatureSection) -> List[str]:
        """Get features that depend on the given section"""
        dependent = []
        for other_section, info in self.feature_sections.items():
            if section.value in info.get("dependencies", []):
                dependent.append(other_section.value)
        return dependent

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status with feature sections"""
        return {
            "timestamp": datetime.now().isoformat(),
            "enabled_features": [
                section.value
                for section, enabled in self.system_state.enabled_sections.items()
                if enabled
            ],
            "disabled_features": [
                section.value
                for section, enabled in self.system_state.enabled_sections.items()
                if not enabled
            ],
            "domain_separation": self.get_domain_separation_guide(),
            "agent_roles": {
                role.value: self.get_agent_role_guide(role) for role in AgentRole
            },
            "working_principles": self.working_principles,
        }

    def get_shutdown_options(self) -> Dict[str, Any]:
        """Get options for shutting down sectional features"""
        return {
            "available_sections": [section.value for section in FeatureSection],
            "shutdown_procedures": self._get_shutdown_procedures(),
            "dependency_map": self._get_feature_dependencies(),
            "impact_assessment": {
                section.value: info["impact"]
                for section, info in self.feature_sections.items()
            },
            "recommended_shutdown_order": self._get_recommended_shutdown_order(),
        }

    def _get_recommended_shutdown_order(self) -> List[str]:
        """Get recommended order for shutting down features"""
        # Order from most dependent to least dependent
        shutdown_order = []
        remaining = set(FeatureSection)

        while remaining:
            # Find features with no remaining dependencies
            ready_to_shutdown = []
            for section in remaining:
                dependencies = self.feature_sections[section].get("dependencies", [])
                if not any(dep in [s.value for s in remaining] for dep in dependencies):
                    ready_to_shutdown.append(section)

            if not ready_to_shutdown:
                # Circular dependency - add remaining in arbitrary order
                ready_to_shutdown = list(remaining)

            for section in ready_to_shutdown:
                shutdown_order.append(section.value)
                remaining.remove(section)

        return shutdown_order


if __name__ == "__main__":
    # Test the master prompt system
    prompt_system = FrenlyMasterPrompt()

    print("=== Master Prompt ===")
    print(prompt_system.get_master_prompt())

    print("\n=== Domain Separation Guide ===")
    print(json.dumps(prompt_system.get_domain_separation_guide(), indent=2))

    print("\n=== Feature Section Control ===")
    print(json.dumps(prompt_system.get_feature_section_control(), indent=2))

    print("\n=== Shutdown Options ===")
    print(json.dumps(prompt_system.get_shutdown_options(), indent=2))

    print("\n=== System Status ===")
    print(json.dumps(prompt_system.get_system_status(), indent=2))
