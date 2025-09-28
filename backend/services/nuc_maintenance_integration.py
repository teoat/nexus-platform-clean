#!/usr/bin/env python3
"""
NUC Maintenance System Integration
Integrates all maintenance components under NUC orchestrator
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import NUC components
from nuc_orchestrator import nuc_orchestrator, ServiceInfo, ServicePriority, ServiceStatus
from nuc_maintenance_controller import maintenance_controller, MaintenanceAction
from intelligent_workspace_cleaner import workspace_cleaner
from file_system_locker import file_system_locker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NUCMaintenanceIntegration:
    """NUC Maintenance System Integration"""
    
    def __init__(self):
        self.running = False
        self.services_registered = False
        self.maintenance_cycle_count = 0
        
        # Statistics
        self.stats = {
            "maintenance_cycles": 0,
            "files_cleaned": 0,
            "files_locked": 0,
            "space_saved": 0,
            "errors": 0,
            "alerts_sent": 0
        }
    
    async def start(self):
        """Start the integrated maintenance system"""
        logger.info("Starting NUC Maintenance Integration...")
        
        try:
            # Start NUC orchestrator
            await nuc_orchestrator.start()
            
            # Register maintenance services
            await self._register_services()
            
            # Start maintenance components
            await maintenance_controller.start()
            await file_system_locker.start()
            
            # Start integrated maintenance loop
            self.running = True
            asyncio.create_task(self._maintenance_loop())
            asyncio.create_task(self._monitoring_loop())
            
            logger.info("NUC Maintenance Integration started successfully")
            
        except Exception as e:
            logger.error(f"Error starting NUC Maintenance Integration: {e}")
            raise
    
    async def stop(self):
        """Stop the integrated maintenance system"""
        logger.info("Stopping NUC Maintenance Integration...")
        
        try:
            self.running = False
            
            # Stop maintenance components
            await maintenance_controller.stop()
            await file_system_locker.stop()
            
            # Stop NUC orchestrator
            await nuc_orchestrator.stop()
            
            logger.info("NUC Maintenance Integration stopped")
            
        except Exception as e:
            logger.error(f"Error stopping NUC Maintenance Integration: {e}")
    
    async def _register_services(self):
        """Register maintenance services with NUC orchestrator"""
        try:
            # Register Maintenance Controller
            maintenance_service = ServiceInfo(
                name="maintenance-controller",
                version="1.0.0",
                status=ServiceStatus.HEALTHY,
                priority=ServicePriority.HIGH,
                health_check_url="http://localhost:8000/health/maintenance",
                dependencies=[],
                metadata={
                    "type": "maintenance",
                    "description": "NUC Maintenance Controller",
                    "endpoints": ["/maintenance/status", "/maintenance/cleanup", "/maintenance/lock"]
                }
            )
            
            # Register Workspace Cleaner
            cleaner_service = ServiceInfo(
                name="workspace-cleaner",
                version="1.0.0",
                status=ServiceStatus.HEALTHY,
                priority=ServicePriority.MEDIUM,
                health_check_url="http://localhost:8000/health/cleaner",
                dependencies=["maintenance-controller"],
                metadata={
                    "type": "cleanup",
                    "description": "Intelligent Workspace Cleaner",
                    "endpoints": ["/cleaner/analyze", "/cleaner/cleanup"]
                }
            )
            
            # Register File System Locker
            locker_service = ServiceInfo(
                name="file-system-locker",
                version="1.0.0",
                status=ServiceStatus.HEALTHY,
                priority=ServicePriority.HIGH,
                health_check_url="http://localhost:8000/health/locker",
                dependencies=["maintenance-controller"],
                metadata={
                    "type": "protection",
                    "description": "File System Locker",
                    "endpoints": ["/locker/status", "/locker/lock", "/locker/unlock"]
                }
            )
            
            # Register services
            nuc_orchestrator.register_service(maintenance_service)
            nuc_orchestrator.register_service(cleaner_service)
            nuc_orchestrator.register_service(locker_service)
            
            self.services_registered = True
            logger.info("Maintenance services registered with NUC orchestrator")
            
        except Exception as e:
            logger.error(f"Error registering services: {e}")
            raise
    
    async def _maintenance_loop(self):
        """Main integrated maintenance loop"""
        while self.running:
            try:
                await self._execute_maintenance_cycle()
                self.maintenance_cycle_count += 1
                self.stats["maintenance_cycles"] += 1
                
                # Wait between cycles (5 minutes)
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in maintenance loop: {e}")
                self.stats["errors"] += 1
                await asyncio.sleep(60)
    
    async def _execute_maintenance_cycle(self):
        """Execute a complete maintenance cycle"""
        logger.info(f"Starting maintenance cycle #{self.maintenance_cycle_count + 1}")
        
        try:
            # Phase 1: Analyze workspace
            logger.info("Phase 1: Analyzing workspace...")
            analysis_report = await workspace_cleaner.analyze_workspace()
            
            # Phase 2: Apply file locks
            logger.info("Phase 2: Applying file locks...")
            await file_system_locker._apply_all_rules()
            
            # Phase 3: Execute cleanup
            logger.info("Phase 3: Executing cleanup...")
            cleanup_results = await workspace_cleaner.execute_cleanup(dry_run=False)
            
            # Phase 4: Update statistics
            logger.info("Phase 4: Updating statistics...")
            self._update_stats(analysis_report, cleanup_results)
            
            # Phase 5: Send notifications
            logger.info("Phase 5: Sending notifications...")
            await self._send_maintenance_notifications(analysis_report, cleanup_results)
            
            logger.info(f"Maintenance cycle #{self.maintenance_cycle_count + 1} completed")
            
        except Exception as e:
            logger.error(f"Error in maintenance cycle: {e}")
            self.stats["errors"] += 1
    
    async def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                await self._monitor_system_health()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_system_health(self):
        """Monitor system health and send alerts"""
        try:
            # Get NUC system health
            nuc_health = nuc_orchestrator.get_system_health()
            
            # Get maintenance controller status
            maintenance_status = maintenance_controller.get_status()
            
            # Get file system locker status
            locker_status = file_system_locker.get_status()
            
            # Check for issues
            if nuc_health["overall_health"] < 80:
                await self._send_alert("NUC System Health Low", {
                    "overall_health": nuc_health["overall_health"],
                    "healthy_services": nuc_health["healthy_services"],
                    "total_services": nuc_health["total_services"]
                })
            
            if maintenance_status["stats"]["errors"] > 10:
                await self._send_alert("Maintenance Controller Errors", {
                    "error_count": maintenance_status["stats"]["errors"],
                    "files_processed": maintenance_status["stats"]["files_processed"]
                })
            
            if locker_status["stats"]["protection_violations"] > 0:
                await self._send_alert("File Protection Violations", {
                    "violation_count": locker_status["stats"]["protection_violations"],
                    "protected_files": locker_status["protected_files"]
                })
                
        except Exception as e:
            logger.error(f"Error monitoring system health: {e}")
    
    def _update_stats(self, analysis_report: Dict[str, Any], cleanup_results: Dict[str, Any]):
        """Update maintenance statistics"""
        try:
            # Update from analysis report
            if "stats" in analysis_report:
                self.stats["files_cleaned"] += analysis_report["stats"].get("files_cleaned", 0)
                self.stats["space_saved"] += analysis_report["stats"].get("space_saved", 0)
            
            # Update from cleanup results
            if "files_cleaned" in cleanup_results:
                self.stats["files_cleaned"] += cleanup_results["files_cleaned"]
            if "space_saved" in cleanup_results:
                self.stats["space_saved"] += cleanup_results["space_saved"]
            if "errors" in cleanup_results:
                self.stats["errors"] += cleanup_results["errors"]
                
        except Exception as e:
            logger.error(f"Error updating stats: {e}")
    
    async def _send_maintenance_notifications(self, analysis_report: Dict[str, Any], cleanup_results: Dict[str, Any]):
        """Send maintenance notifications"""
        try:
            # Create notification summary
            notification = {
                "timestamp": datetime.now().isoformat(),
                "cycle": self.maintenance_cycle_count + 1,
                "summary": {
                    "files_analyzed": analysis_report.get("summary", {}).get("total_files", 0),
                    "files_cleaned": cleanup_results.get("files_cleaned", 0),
                    "space_saved_mb": cleanup_results.get("space_saved", 0) / (1024 * 1024),
                    "errors": cleanup_results.get("errors", 0)
                },
                "recommendations": analysis_report.get("recommendations", [])
            }
            
            # Log notification
            logger.info(f"Maintenance notification: {json.dumps(notification, indent=2)}")
            
            # In production, this would send to external notification systems
            # For now, we'll just log it
            
        except Exception as e:
            logger.error(f"Error sending maintenance notifications: {e}")
    
    async def _send_alert(self, alert_type: str, data: Dict[str, Any]):
        """Send system alert"""
        try:
            alert = {
                "timestamp": datetime.now().isoformat(),
                "type": alert_type,
                "data": data,
                "severity": "warning"
            }
            
            logger.warning(f"System Alert: {json.dumps(alert, indent=2)}")
            self.stats["alerts_sent"] += 1
            
            # In production, this would send to external alerting systems
            
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_integrated_status(self) -> Dict[str, Any]:
        """Get integrated system status"""
        try:
            return {
                "running": self.running,
                "services_registered": self.services_registered,
                "maintenance_cycles": self.maintenance_cycle_count,
                "nuc_health": nuc_orchestrator.get_system_health(),
                "maintenance_status": maintenance_controller.get_status(),
                "locker_status": file_system_locker.get_status(),
                "cleaner_status": workspace_cleaner.stats,
                "integration_stats": self.stats
            }
        except Exception as e:
            logger.error(f"Error getting integrated status: {e}")
            return {"error": str(e)}
    
    async def force_cleanup(self, dry_run: bool = True) -> Dict[str, Any]:
        """Force immediate cleanup"""
        try:
            logger.info(f"Force cleanup requested (dry_run={dry_run})")
            
            # Analyze workspace
            analysis_report = await workspace_cleaner.analyze_workspace()
            
            # Execute cleanup
            cleanup_results = await workspace_cleaner.execute_cleanup(dry_run=dry_run)
            
            # Update stats
            self._update_stats(analysis_report, cleanup_results)
            
            return {
                "analysis": analysis_report,
                "cleanup": cleanup_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in force cleanup: {e}")
            return {"error": str(e)}
    
    async def force_lock(self, pattern: str = None) -> Dict[str, Any]:
        """Force immediate file locking"""
        try:
            logger.info(f"Force lock requested (pattern={pattern})")
            
            if pattern:
                # Create temporary rule for specific pattern
                from file_system_locker import LockRule, LockType, LockLevel
                
                temp_rule = LockRule(
                    id="force_lock_temp",
                    name="Force Lock Temporary",
                    pattern=pattern,
                    lock_type=LockType.READONLY,
                    level=LockLevel.HIGH,
                    enabled=True,
                    auto_apply=True
                )
                
                file_system_locker.add_lock_rule(temp_rule)
                await file_system_locker._apply_rule(temp_rule)
                file_system_locker.remove_lock_rule("force_lock_temp")
            else:
                # Apply all existing rules
                await file_system_locker._apply_all_rules()
            
            return {
                "locked_files": file_system_locker.get_locked_files(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in force lock: {e}")
            return {"error": str(e)}


# Global integration instance
nuc_maintenance_integration = NUCMaintenanceIntegration()


async def main():
    """Main entry point for testing"""
    try:
        # Start integrated system
        await nuc_maintenance_integration.start()
        
        # Wait for some maintenance cycles
        await asyncio.sleep(600)  # 10 minutes
        
        # Show integrated status
        status = nuc_maintenance_integration.get_integrated_status()
        print(f"NUC Maintenance Integration Status: {json.dumps(status, indent=2)}")
        
        # Test force cleanup
        cleanup_result = await nuc_maintenance_integration.force_cleanup(dry_run=True)
        print(f"Force Cleanup Result: {json.dumps(cleanup_result, indent=2)}")
        
        # Test force lock
        lock_result = await nuc_maintenance_integration.force_lock("*.log")
        print(f"Force Lock Result: {json.dumps(lock_result, indent=2)}")
        
        # Stop integrated system
        await nuc_maintenance_integration.stop()
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
