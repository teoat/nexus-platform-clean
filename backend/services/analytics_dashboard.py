#!/usr/bin/env python3
"""
NUC Advanced Analytics Dashboard
Provides comprehensive analytics and intelligence for workspace management
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WorkspaceMetrics:
    """Workspace health metrics"""
    total_files: int = 0
    total_size_mb: float = 0.0
    ssot_files: int = 0
    locked_files: int = 0
    cleanup_operations: int = 0
    space_saved_mb: float = 0.0
    last_cleanup: Optional[datetime] = None
    health_score: float = 0.0
    trends: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileAnalytics:
    """File usage analytics"""
    path: str
    size_mb: float
    last_accessed: datetime
    access_count: int = 0
    importance_score: float = 0.0
    category: str = "unknown"
    dependencies: List[str] = field(default_factory=list)


class AdvancedAnalyticsDashboard:
    """Advanced Analytics Dashboard for NUC Workspace Management"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "analytics.db"
        self.metrics_history: List[WorkspaceMetrics] = []
        
        # Initialize database
        self._init_database()
        
        # Analytics configuration
        self.analytics_config = {
            "health_score_weights": {
                "file_organization": 0.3,
                "space_efficiency": 0.25,
                "ssot_coverage": 0.2,
                "security_compliance": 0.15,
                "maintenance_frequency": 0.1
            },
            "importance_factors": {
                "access_frequency": 0.4,
                "file_size": 0.2,
                "dependency_count": 0.2,
                "category_criticality": 0.2
            }
        }
    
    def _init_database(self):
        """Initialize analytics database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Workspace metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workspace_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                total_files INTEGER,
                total_size_mb REAL,
                ssot_files INTEGER,
                locked_files INTEGER,
                cleanup_operations INTEGER,
                space_saved_mb REAL,
                health_score REAL,
                metrics_data TEXT
            )
        """)
        
        # File analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_analytics (
                path TEXT PRIMARY KEY,
                size_mb REAL,
                last_accessed TEXT,
                access_count INTEGER DEFAULT 0,
                importance_score REAL DEFAULT 0.0,
                category TEXT,
                dependencies TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Operations log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS operations_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation_type TEXT,
                operation_details TEXT,
                success BOOLEAN,
                impact_score REAL,
                duration_seconds REAL
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def collect_workspace_metrics(self) -> WorkspaceMetrics:
        """Collect comprehensive workspace metrics"""
        logger.info("📊 Collecting workspace metrics...")
        
        try:
            metrics = WorkspaceMetrics()
            
            # Basic file statistics
            total_size = 0
            file_count = 0
            
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    try:
                        stat_info = file_path.stat()
                        total_size += stat_info.st_size
                        file_count += 1
                    except Exception as e:
                        logger.warning(f"Could not analyze {file_path}: {e}")
            
            metrics.total_files = file_count
            metrics.total_size_mb = total_size / (1024 * 1024)
            
            # SSOT and locked file counts
            ssot_db_path = self.base_path / "data" / "ssot_files.db"
            if ssot_db_path.exists():
                conn = sqlite3.connect(str(ssot_db_path))
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM ssot_files")
                metrics.ssot_files = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM ssot_files WHERE locked = TRUE")
                metrics.locked_files = cursor.fetchone()[0]
                
                conn.close()
            
            # Calculate health score
            metrics.health_score = await self._calculate_health_score(metrics)
            
            # Store metrics
            await self._store_metrics(metrics)
            
            logger.info(f"✅ Collected metrics: {metrics.total_files} files, {metrics.total_size_mb:.2f} MB, health score: {metrics.health_score:.2f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting workspace metrics: {e}")
            return WorkspaceMetrics()
    
    async def _calculate_health_score(self, metrics: WorkspaceMetrics) -> float:
        """Calculate workspace health score"""
        try:
            weights = self.analytics_config["health_score_weights"]
            score = 0.0
            
            # File organization score (based on SSOT coverage)
            if metrics.total_files > 0:
                ssot_coverage = metrics.ssot_files / metrics.total_files
                score += weights["file_organization"] * min(ssot_coverage * 2, 1.0)
            
            # Space efficiency score (based on cleanup operations)
            if metrics.total_size_mb > 0:
                space_efficiency = min(metrics.space_saved_mb / metrics.total_size_mb * 10, 1.0)
                score += weights["space_efficiency"] * space_efficiency
            
            # SSOT coverage score
            if metrics.total_files > 0:
                ssot_score = min(metrics.ssot_files / metrics.total_files * 3, 1.0)
                score += weights["ssot_coverage"] * ssot_score
            
            # Security compliance score (based on locked files)
            if metrics.ssot_files > 0:
                security_score = metrics.locked_files / metrics.ssot_files
                score += weights["security_compliance"] * security_score
            
            # Maintenance frequency score
            if metrics.last_cleanup:
                days_since_cleanup = (datetime.now() - metrics.last_cleanup).days
                maintenance_score = max(0, 1 - (days_since_cleanup / 30))
                score += weights["maintenance_frequency"] * maintenance_score
            
            return min(score, 1.0) * 100  # Convert to percentage
            
        except Exception as e:
            logger.error(f"Error calculating health score: {e}")
            return 0.0
    
    async def analyze_file_importance(self) -> List[FileAnalytics]:
        """Analyze file importance and usage patterns"""
        logger.info("🔍 Analyzing file importance...")
        
        try:
            file_analytics = []
            
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    try:
                        stat_info = file_path.stat()
                        relative_path = str(file_path.relative_to(self.base_path))
                        
                        analytics = FileAnalytics(
                            path=relative_path,
                            size_mb=stat_info.st_size / (1024 * 1024),
                            last_accessed=datetime.fromtimestamp(stat_info.st_atime),
                            access_count=0,  # Would need file system monitoring
                            importance_score=0.0,
                            category=self._categorize_file(relative_path)
                        )
                        
                        # Calculate importance score
                        analytics.importance_score = await self._calculate_importance_score(analytics)
                        
                        file_analytics.append(analytics)
                        
                    except Exception as e:
                        logger.warning(f"Could not analyze {file_path}: {e}")
            
            # Sort by importance score
            file_analytics.sort(key=lambda x: x.importance_score, reverse=True)
            
            logger.info(f"✅ Analyzed {len(file_analytics)} files")
            return file_analytics
            
        except Exception as e:
            logger.error(f"Error analyzing file importance: {e}")
            return []
    
    def _categorize_file(self, file_path: str) -> str:
        """Categorize file based on path and extension"""
        if any(pattern in file_path for pattern in ["package.json", "requirements.txt", "docker-compose"]):
            return "configuration"
        elif any(pattern in file_path for pattern in [".py", ".ts", ".tsx", ".js", ".jsx"]):
            return "source_code"
        elif any(pattern in file_path for pattern in [".md", "README", "docs/"]):
            return "documentation"
        elif any(pattern in file_path for pattern in [".db", ".sqlite", ".sql"]):
            return "database"
        elif any(pattern in file_path for pattern in ["Dockerfile", "docker/", "k8s/"]):
            return "deployment"
        elif any(pattern in file_path for pattern in [".env", ".key", ".pem"]):
            return "security"
        else:
            return "other"
    
    async def _calculate_importance_score(self, analytics: FileAnalytics) -> float:
        """Calculate file importance score"""
        try:
            factors = self.analytics_config["importance_factors"]
            score = 0.0
            
            # Access frequency factor
            score += factors["access_frequency"] * min(analytics.access_count / 10, 1.0)
            
            # File size factor (larger files often more important)
            score += factors["file_size"] * min(analytics.size_mb / 10, 1.0)
            
            # Dependency count factor
            score += factors["dependency_count"] * min(len(analytics.dependencies) / 5, 1.0)
            
            # Category criticality factor
            category_scores = {
                "configuration": 1.0,
                "source_code": 0.9,
                "database": 0.8,
                "security": 0.9,
                "deployment": 0.7,
                "documentation": 0.5,
                "other": 0.3
            }
            score += factors["category_criticality"] * category_scores.get(analytics.category, 0.3)
            
            return min(score, 1.0) * 100  # Convert to percentage
            
        except Exception as e:
            logger.error(f"Error calculating importance score: {e}")
            return 0.0
    
    async def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        logger.info("💡 Generating optimization recommendations...")
        
        try:
            recommendations = []
            metrics = await self.collect_workspace_metrics()
            file_analytics = await self.analyze_file_importance()
            
            # Space optimization recommendations
            large_files = [f for f in file_analytics if f.size_mb > 10]
            if large_files:
                recommendations.append({
                    "type": "space_optimization",
                    "priority": "high",
                    "title": "Large Files Detected",
                    "description": f"Found {len(large_files)} files larger than 10MB",
                    "action": "Consider archiving or compressing large files",
                    "files": [f.path for f in large_files[:5]]  # Top 5
                })
            
            # SSOT coverage recommendations
            if metrics.total_files > 0:
                ssot_coverage = metrics.ssot_files / metrics.total_files
                if ssot_coverage < 0.3:
                    recommendations.append({
                        "type": "ssot_coverage",
                        "priority": "medium",
                        "title": "Low SSOT Coverage",
                        "description": f"Only {ssot_coverage:.1%} of files are marked as SSOT",
                        "action": "Consider marking more critical files as SSOT",
                        "coverage_percentage": ssot_coverage
                    })
            
            # Security recommendations
            if metrics.ssot_files > 0:
                lock_coverage = metrics.locked_files / metrics.ssot_files
                if lock_coverage < 0.8:
                    recommendations.append({
                        "type": "security",
                        "priority": "high",
                        "title": "Incomplete File Locking",
                        "description": f"Only {lock_coverage:.1%} of SSOT files are locked",
                        "action": "Lock remaining SSOT files for security",
                        "unlocked_count": metrics.ssot_files - metrics.locked_files
                    })
            
            # Maintenance recommendations
            if metrics.last_cleanup:
                days_since_cleanup = (datetime.now() - metrics.last_cleanup).days
                if days_since_cleanup > 7:
                    recommendations.append({
                        "type": "maintenance",
                        "priority": "medium",
                        "title": "Overdue Maintenance",
                        "description": f"Last cleanup was {days_since_cleanup} days ago",
                        "action": "Run cleanup operations to maintain workspace health",
                        "days_overdue": days_since_cleanup
                    })
            
            logger.info(f"✅ Generated {len(recommendations)} optimization recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    async def generate_analytics_report(self) -> Dict[str, Any]:
        """Generate comprehensive analytics report"""
        logger.info("📊 Generating comprehensive analytics report...")
        
        try:
            metrics = await self.collect_workspace_metrics()
            file_analytics = await self.analyze_file_importance()
            recommendations = await self.generate_optimization_recommendations()
            
            # Calculate trends
            trends = await self._calculate_trends()
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "workspace_metrics": {
                    "total_files": metrics.total_files,
                    "total_size_mb": metrics.total_size_mb,
                    "ssot_files": metrics.ssot_files,
                    "locked_files": metrics.locked_files,
                    "health_score": metrics.health_score,
                    "cleanup_operations": metrics.cleanup_operations,
                    "space_saved_mb": metrics.space_saved_mb
                },
                "file_analytics": {
                    "total_analyzed": len(file_analytics),
                    "top_files": [
                        {
                            "path": f.path,
                            "size_mb": f.size_mb,
                            "importance_score": f.importance_score,
                            "category": f.category
                        }
                        for f in file_analytics[:10]
                    ],
                    "category_distribution": self._get_category_distribution(file_analytics)
                },
                "trends": trends,
                "recommendations": recommendations,
                "health_assessment": self._assess_workspace_health(metrics)
            }
            
            # Save report
            report_file = self.base_path / "analytics_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"✅ Analytics report saved to {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {}
    
    async def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate trends from historical data"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Get last 7 days of metrics
            cursor.execute("""
                SELECT * FROM workspace_metrics 
                WHERE timestamp >= datetime('now', '-7 days')
                ORDER BY timestamp DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 2:
                return {"status": "insufficient_data"}
            
            # Calculate trends
            latest = rows[0]
            previous = rows[-1]
            
            trends = {
                "file_count_change": latest[2] - previous[2],
                "size_change_mb": latest[3] - previous[3],
                "health_score_change": latest[8] - previous[8],
                "trend_period_days": 7,
                "data_points": len(rows)
            }
            
            return trends
            
        except Exception as e:
            logger.error(f"Error calculating trends: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_category_distribution(self, file_analytics: List[FileAnalytics]) -> Dict[str, int]:
        """Get distribution of files by category"""
        distribution = {}
        for analytics in file_analytics:
            category = analytics.category
            distribution[category] = distribution.get(category, 0) + 1
        return distribution
    
    def _assess_workspace_health(self, metrics: WorkspaceMetrics) -> Dict[str, Any]:
        """Assess overall workspace health"""
        health_level = "excellent"
        if metrics.health_score < 70:
            health_level = "good"
        if metrics.health_score < 50:
            health_level = "fair"
        if metrics.health_score < 30:
            health_level = "poor"
        
        return {
            "overall_health": health_level,
            "health_score": metrics.health_score,
            "key_metrics": {
                "ssot_coverage": metrics.ssot_files / max(metrics.total_files, 1),
                "lock_coverage": metrics.locked_files / max(metrics.ssot_files, 1),
                "space_efficiency": metrics.space_saved_mb / max(metrics.total_size_mb, 1)
            }
        }
    
    async def _store_metrics(self, metrics: WorkspaceMetrics):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO workspace_metrics 
                (timestamp, total_files, total_size_mb, ssot_files, locked_files, 
                 cleanup_operations, space_saved_mb, health_score, metrics_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                metrics.total_files,
                metrics.total_size_mb,
                metrics.ssot_files,
                metrics.locked_files,
                metrics.cleanup_operations,
                metrics.space_saved_mb,
                metrics.health_score,
                json.dumps(metrics.trends, default=str)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")


# Global analytics dashboard instance
analytics_dashboard = AdvancedAnalyticsDashboard()


async def main():
    """Main entry point for testing"""
    try:
        # Generate comprehensive analytics report
        report = await analytics_dashboard.generate_analytics_report()
        
        print("📊 ANALYTICS DASHBOARD REPORT")
        print("=" * 50)
        print(f"Workspace Health Score: {report.get('workspace_metrics', {}).get('health_score', 0):.1f}")
        print(f"Total Files: {report.get('workspace_metrics', {}).get('total_files', 0)}")
        print(f"SSOT Files: {report.get('workspace_metrics', {}).get('ssot_files', 0)}")
        print(f"Locked Files: {report.get('workspace_metrics', {}).get('locked_files', 0)}")
        print(f"Recommendations: {len(report.get('recommendations', []))}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
