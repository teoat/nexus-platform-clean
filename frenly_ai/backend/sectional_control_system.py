#!/usr/bin/env python3
"""
Sectional Control System
Manages enabling/disabling of Frenly AI feature sections
"""

import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ControlAction(Enum):
    """Control actions for feature sections"""

    ENABLE = "enable"
    DISABLE = "disable"
    RESTART = "restart"
    STATUS = "status"


@dataclass
class SectionalControl:
    """Control configuration for a feature section"""

    section: FeatureSection
    enabled: bool
    dependencies: List[FeatureSection]
    dependents: List[FeatureSection]
    impact_level: str
    shutdown_effects: List[str]
    restart_required: bool


class SectionalControlSystem:
    """System for managing Frenly AI feature sections"""

    def __init__(self):
        self.master_prompt = FrenlyMasterPrompt()
        self.sectional_controls = self._initialize_sectional_controls()
        self.control_handlers = self._setup_control_handlers()
        self.system_state = {
            "last_control_action": None,
            "control_history": [],
            "system_health": "healthy",
        }

    def _initialize_sectional_controls(self) -> Dict[FeatureSection, SectionalControl]:
        """Initialize sectional control configurations"""
        controls = {}

        for section in FeatureSection:
            section_info = self.master_prompt.feature_sections[section]
            controls[section] = SectionalControl(
                section=section,
                enabled=section_info["enabled"],
                dependencies=[
                    FeatureSection(dep) for dep in section_info.get("dependencies", [])
                ],
                dependents=[],  # Will be populated later
                impact_level=section_info["impact"],
                shutdown_effects=section_info["shutdown_effects"],
                restart_required=section_info["impact"] == "high",
            )

        # Populate dependents
        for section, control in controls.items():
            for other_section, other_control in controls.items():
                if section in other_control.dependencies:
                    control.dependents.append(other_section)

        return controls

    def _setup_control_handlers(self) -> Dict[FeatureSection, Callable]:
        """Setup control handlers for each feature section"""
        return {
            FeatureSection.STRUCTURAL_ANALYSIS: self._handle_structural_analysis_control,
            FeatureSection.DYNAMIC_COLLABORATION: self._handle_dynamic_collaboration_control,
            FeatureSection.AUTOMATION_PROPOSALS: self._handle_automation_proposals_control,
            FeatureSection.LOAD_BALANCING: self._handle_load_balancing_control,
            FeatureSection.GEMINI_CLI_INTEGRATION: self._handle_gemini_cli_control,
            FeatureSection.QUALITY_CONTROL: self._handle_quality_control_control,
            FeatureSection.SELF_HEALING: self._handle_self_healing_control,
            FeatureSection.REAL_TIME_MONITORING: self._handle_real_time_monitoring_control,
        }

    async def control_feature_section(
        self, section: FeatureSection, action: ControlAction
    ) -> Dict[str, Any]:
        """Control a feature section (enable/disable/restart/status)"""
        logger.info(f"🎛️ Controlling {section.value}: {action.value}")

        if action == ControlAction.STATUS:
            return await self._get_section_status(section)

        if action == ControlAction.ENABLE:
            return await self._enable_section(section)
        elif action == ControlAction.DISABLE:
            return await self._disable_section(section)
        elif action == ControlAction.RESTART:
            return await self._restart_section(section)

        return {"error": f"Unknown action: {action.value}"}

    async def _get_section_status(self, section: FeatureSection) -> Dict[str, Any]:
        """Get status of a feature section"""
        control = self.sectional_controls[section]

        return {
            "section": section.value,
            "enabled": control.enabled,
            "dependencies": [dep.value for dep in control.dependencies],
            "dependents": [dep.value for dep in control.dependents],
            "impact_level": control.impact_level,
            "restart_required": control.restart_required,
            "shutdown_effects": control.shutdown_effects,
        }

    async def _enable_section(self, section: FeatureSection) -> Dict[str, Any]:
        """Enable a feature section"""
        control = self.sectional_controls[section]

        if control.enabled:
            return {"status": "already_enabled", "section": section.value}

        # Check if dependencies are enabled
        missing_dependencies = []
        for dep in control.dependencies:
            if not self.sectional_controls[dep].enabled:
                missing_dependencies.append(dep.value)

        if missing_dependencies:
            return {
                "status": "failed",
                "section": section.value,
                "error": f"Missing dependencies: {missing_dependencies}",
                "required_dependencies": missing_dependencies,
            }

        # Enable the section
        control.enabled = True
        self.master_prompt.enable_feature_section(section)

        # Execute control handler
        if section in self.control_handlers:
            await self.control_handlers[section](ControlAction.ENABLE)

        # Log control action
        self._log_control_action(section, ControlAction.ENABLE, "success")

        return {
            "status": "enabled",
            "section": section.value,
            "restart_required": control.restart_required,
            "impact_level": control.impact_level,
        }

    async def _disable_section(self, section: FeatureSection) -> Dict[str, Any]:
        """Disable a feature section"""
        control = self.sectional_controls[section]

        if not control.enabled:
            return {"status": "already_disabled", "section": section.value}

        # Check if dependents are enabled
        enabled_dependents = []
        for dep in control.dependents:
            if self.sectional_controls[dep].enabled:
                enabled_dependents.append(dep.value)

        if enabled_dependents:
            return {
                "status": "failed",
                "section": section.value,
                "error": f"Cannot disable: {enabled_dependents} depend on this section",
                "blocking_dependents": enabled_dependents,
            }

        # Disable the section
        control.enabled = False
        self.master_prompt.disable_feature_section(section)

        # Execute control handler
        if section in self.control_handlers:
            await self.control_handlers[section](ControlAction.DISABLE)

        # Log control action
        self._log_control_action(section, ControlAction.DISABLE, "success")

        return {
            "status": "disabled",
            "section": section.value,
            "shutdown_effects": control.shutdown_effects,
            "impact_level": control.impact_level,
        }

    async def _restart_section(self, section: FeatureSection) -> Dict[str, Any]:
        """Restart a feature section"""
        control = self.sectional_controls[section]

        if not control.enabled:
            return {
                "status": "failed",
                "section": section.value,
                "error": "Section is disabled",
            }

        # Execute restart handler
        if section in self.control_handlers:
            await self.control_handlers[section](ControlAction.RESTART)

        # Log control action
        self._log_control_action(section, ControlAction.RESTART, "success")

        return {
            "status": "restarted",
            "section": section.value,
            "restart_required": control.restart_required,
        }

    def _log_control_action(
        self, section: FeatureSection, action: ControlAction, result: str
    ):
        """Log a control action"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "section": section.value,
            "action": action.value,
            "result": result,
        }

        self.system_state["control_history"].append(log_entry)
        self.system_state["last_control_action"] = log_entry

        # Keep only last 100 actions
        if len(self.system_state["control_history"]) > 100:
            self.system_state["control_history"] = self.system_state["control_history"][
                -100:
            ]

    # Control handlers for each feature section
    async def _handle_structural_analysis_control(self, action: ControlAction):
        """Handle structural analysis control"""
        if action == ControlAction.ENABLE:
            logger.info("🔍 Enabling structural analysis - starting project scanning")
            # Start continuous project structure analysis
        elif action == ControlAction.DISABLE:
            logger.info("🔍 Disabling structural analysis - stopping project scanning")
            # Stop project structure analysis
        elif action == ControlAction.RESTART:
            logger.info(
                "🔍 Restarting structural analysis - clearing cache and rescanning"
            )
            # Clear analysis cache and restart scanning

    async def _handle_dynamic_collaboration_control(self, action: ControlAction):
        """Handle dynamic collaboration control"""
        if action == ControlAction.ENABLE:
            logger.info(
                "🤝 Enabling dynamic collaboration - starting agent communication"
            )
            # Start agent collaboration protocols
        elif action == ControlAction.DISABLE:
            logger.info(
                "🤝 Disabling dynamic collaboration - stopping agent communication"
            )
            # Stop agent collaboration protocols
        elif action == ControlAction.RESTART:
            logger.info(
                "🤝 Restarting dynamic collaboration - resetting agent connections"
            )
            # Reset agent connections and restart collaboration

    async def _handle_automation_proposals_control(self, action: ControlAction):
        """Handle automation proposals control"""
        if action == ControlAction.ENABLE:
            logger.info(
                "⚙️ Enabling automation proposals - starting proposal generation"
            )
            # Start automation proposal generation
        elif action == ControlAction.DISABLE:
            logger.info(
                "⚙️ Disabling automation proposals - stopping proposal generation"
            )
            # Stop automation proposal generation
        elif action == ControlAction.RESTART:
            logger.info("⚙️ Restarting automation proposals - clearing proposal cache")
            # Clear proposal cache and restart generation

    async def _handle_load_balancing_control(self, action: ControlAction):
        """Handle load balancing control"""
        if action == ControlAction.ENABLE:
            logger.info("⚖️ Enabling load balancing - starting workload distribution")
            # Start load balancing algorithms
        elif action == ControlAction.DISABLE:
            logger.info("⚖️ Disabling load balancing - stopping workload distribution")
            # Stop load balancing algorithms
        elif action == ControlAction.RESTART:
            logger.info("⚖️ Restarting load balancing - resetting workload metrics")
            # Reset workload metrics and restart balancing

    async def _handle_gemini_cli_control(self, action: ControlAction):
        """Handle Gemini CLI integration control"""
        if action == ControlAction.ENABLE:
            logger.info("🔧 Enabling Gemini CLI integration - starting CLI monitoring")
            # Start Gemini CLI integration
        elif action == ControlAction.DISABLE:
            logger.info("🔧 Disabling Gemini CLI integration - stopping CLI monitoring")
            # Stop Gemini CLI integration
        elif action == ControlAction.RESTART:
            logger.info(
                "🔧 Restarting Gemini CLI integration - resetting CLI connections"
            )
            # Reset CLI connections and restart integration

    async def _handle_quality_control_control(self, action: ControlAction):
        """Handle quality control control"""
        if action == ControlAction.ENABLE:
            logger.info("✅ Enabling quality control - starting quality checks")
            # Start quality control processes
        elif action == ControlAction.DISABLE:
            logger.info("✅ Disabling quality control - stopping quality checks")
            # Stop quality control processes
        elif action == ControlAction.RESTART:
            logger.info("✅ Restarting quality control - clearing quality cache")
            # Clear quality cache and restart checks

    async def _handle_self_healing_control(self, action: ControlAction):
        """Handle self-healing control"""
        if action == ControlAction.ENABLE:
            logger.info("🛠️ Enabling self-healing - starting failure detection")
            # Start self-healing processes
        elif action == ControlAction.DISABLE:
            logger.info("🛠️ Disabling self-healing - stopping failure detection")
            # Stop self-healing processes
        elif action == ControlAction.RESTART:
            logger.info("🛠️ Restarting self-healing - resetting health monitoring")
            # Reset health monitoring and restart healing

    async def _handle_real_time_monitoring_control(self, action: ControlAction):
        """Handle real-time monitoring control"""
        if action == ControlAction.ENABLE:
            logger.info("📊 Enabling real-time monitoring - starting status updates")
            # Start real-time monitoring
        elif action == ControlAction.DISABLE:
            logger.info("📊 Disabling real-time monitoring - stopping status updates")
            # Stop real-time monitoring
        elif action == ControlAction.RESTART:
            logger.info("📊 Restarting real-time monitoring - clearing monitoring cache")
            # Clear monitoring cache and restart monitoring

    def get_system_overview(self) -> Dict[str, Any]:
        """Get system overview with sectional controls"""
        enabled_sections = [
            section.value
            for section, control in self.sectional_controls.items()
            if control.enabled
        ]
        disabled_sections = [
            section.value
            for section, control in self.sectional_controls.items()
            if not control.enabled
        ]

        return {
            "timestamp": datetime.now().isoformat(),
            "system_health": self.system_state["system_health"],
            "enabled_sections": enabled_sections,
            "disabled_sections": disabled_sections,
            "total_sections": len(FeatureSection),
            "last_control_action": self.system_state["last_control_action"],
            "control_history_count": len(self.system_state["control_history"]),
        }

    def get_sectional_control_options(self) -> Dict[str, Any]:
        """Get available sectional control options"""
        return {
            "available_actions": [action.value for action in ControlAction],
            "available_sections": [section.value for section in FeatureSection],
            "section_status": {
                section.value: {
                    "enabled": control.enabled,
                    "dependencies": [dep.value for dep in control.dependencies],
                    "dependents": [dep.value for dep in control.dependents],
                    "impact_level": control.impact_level,
                    "can_disable": len(control.dependents) == 0
                    or not any(
                        self.sectional_controls[dep].enabled
                        for dep in control.dependents
                    ),
                    "can_enable": all(
                        self.sectional_controls[dep].enabled
                        for dep in control.dependencies
                    ),
                }
                for section, control in self.sectional_controls.items()
            },
            "recommended_shutdown_order": self.master_prompt._get_recommended_shutdown_order(),
        }

    async def bulk_control(self, actions: List[Dict[str, str]]) -> Dict[str, Any]:
        """Execute multiple control actions in sequence"""
        results = []

        for action_data in actions:
            section = FeatureSection(action_data["section"])
            action = ControlAction(action_data["action"])

            result = await self.control_feature_section(section, action)
            results.append(
                {"section": section.value, "action": action.value, "result": result}
            )

        return {
            "bulk_actions": results,
            "total_actions": len(actions),
            "successful_actions": len(
                [
                    r
                    for r in results
                    if r["result"].get("status")
                    in [
                        "enabled",
                        "disabled",
                        "restarted",
                        "already_enabled",
                        "already_disabled",
                    ]
                ]
            ),
            "failed_actions": len(
                [r for r in results if r["result"].get("status") == "failed"]
            ),
        }


if __name__ == "__main__":
    # Test the sectional control system
    async def test_system():
        control_system = SectionalControlSystem()

        print("=== System Overview ===")
        print(json.dumps(control_system.get_system_overview(), indent=2))

        print("\n=== Sectional Control Options ===")
        print(json.dumps(control_system.get_sectional_control_options(), indent=2))

        print("\n=== Test Disable Structural Analysis ===")
        result = await control_system.control_feature_section(
            FeatureSection.STRUCTURAL_ANALYSIS, ControlAction.DISABLE
        )
        print(json.dumps(result, indent=2))

        print("\n=== Test Enable Structural Analysis ===")
        result = await control_system.control_feature_section(
            FeatureSection.STRUCTURAL_ANALYSIS, ControlAction.ENABLE
        )
        print(json.dumps(result, indent=2))

    asyncio.run(test_system())
