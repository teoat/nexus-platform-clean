"""
Modular Automation System - NEXUS Platform
Discrete, reusable automation modules for Frenly AI orchestration
"""

from .background_optimizer import BackgroundOptimizer
from .dependency_optimizer import DependencyOptimizer
from .file_management import FileManagementModule
from .file_optimizer import FileOptimizer
from .frenly_ai_meta import FrenlyAIMetaModule
from .optimization import OptimizationModule
from .optimization_orchestrator import OptimizationOrchestrator
from .repo_pruner import RepoPruner

__all__ = [
    "FileManagementModule",
    "OptimizationModule",
    "FileOptimizer",
    "DependencyOptimizer",
    "RepoPruner",
    "BackgroundOptimizer",
    "OptimizationOrchestrator",
    "FrenlyAIMetaModule",
]

# Module registry for dynamic loading
MODULE_REGISTRY = {
    "file_management": FileManagementModule,
    "optimization": OptimizationModule,
    "file_optimizer": FileOptimizer,
    "dependency_optimizer": DependencyOptimizer,
    "repo_pruner": RepoPruner,
    "background_optimizer": BackgroundOptimizer,
    "optimization_orchestrator": OptimizationOrchestrator,
    "frenly_ai_meta": FrenlyAIMetaModule,
}
