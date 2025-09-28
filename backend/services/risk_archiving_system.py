#!/usr/bin/env python3
"""
NUC Risk-Based Archiving System
Intelligently archives medium-risk files to archived_bin folder with comprehensive management
"""

import asyncio
import json
import logging
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for file archiving"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ArchiveStatus(Enum):
    """Archive status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    RESTORED = "restored"
    DELETED = "deleted"


@dataclass
class FileRiskAssessment:
    """File risk assessment"""
    path: str
    size_mb: float
    risk_level: RiskLevel
    risk_score: float
    risk_factors: List[str]
    last_accessed: datetime
    importance_score: float
    category: str
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ArchiveRecord:
    """Archive record"""
    archive_id: str
    original_path: str
    archive_path: str
    archived_at: datetime
    risk_level: RiskLevel
    risk_score: float
    file_size_mb: float
    status: ArchiveStatus
    expires_at: Optional[datetime] = None
    restored_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class RiskBasedArchivingSystem:
    """Risk-Based Archiving System for NUC Workspace Management"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.archived_bin = self.base_path / "archived_bin"
        self.db_path = self.base_path / "data" / "archiving_system.db"
        self.archive_records: List[ArchiveRecord] = []
        
        # Initialize database and directories
        self._init_database()
        self._init_archive_structure()
        
        # Risk assessment configuration
        self.risk_config = {
            "risk_thresholds": {
                "low": 0.3,
                "medium": 0.6,
                "high": 0.8,
                "critical": 0.9
            },
            "archive_policies": {
                "medium_risk": {
                    "archive_immediately": True,
                    "retention_days": 30,
                    "auto_delete": False
                },
                "high_risk": {
                    "archive_immediately": False,
                    "retention_days": 90,
                    "auto_delete": False
                },
                "low_risk": {
                    "archive_immediately": False,
                    "retention_days": 7,
                    "auto_delete": True
                }
            },
            "file_categories": {
                "logs": {"risk_multiplier": 0.8, "archive_priority": "high"},
                "temp": {"risk_multiplier": 0.9, "archive_priority": "high"},
                "cache": {"risk_multiplier": 0.9, "archive_priority": "high"},
                "backup": {"risk_multiplier": 0.7, "archive_priority": "medium"},
                "documentation": {"risk_multiplier": 0.4, "archive_priority": "low"},
                "source_code": {"risk_multiplier": 0.2, "archive_priority": "low"},
                "configuration": {"risk_multiplier": 0.1, "archive_priority": "low"}
            }
        }
        
        # Load existing archive records
        self._load_archive_records()
    
    def _init_database(self):
        """Initialize archiving system database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Archive records table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archive_records (
                archive_id TEXT PRIMARY KEY,
                original_path TEXT NOT NULL,
                archive_path TEXT NOT NULL,
                archived_at TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                risk_score REAL NOT NULL,
                file_size_mb REAL NOT NULL,
                status TEXT NOT NULL,
                expires_at TEXT,
                restored_at TEXT,
                metadata TEXT
            )
        """)
        
        # Risk assessments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS risk_assessments (
                file_path TEXT PRIMARY KEY,
                risk_level TEXT NOT NULL,
                risk_score REAL NOT NULL,
                risk_factors TEXT NOT NULL,
                importance_score REAL NOT NULL,
                category TEXT NOT NULL,
                last_assessed TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_archive_structure(self):
        """Initialize archive folder structure"""
        self.archived_bin.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.archived_bin / "medium_risk").mkdir(exist_ok=True)
        (self.archived_bin / "high_risk").mkdir(exist_ok=True)
        (self.archived_bin / "expired").mkdir(exist_ok=True)
        (self.archived_bin / "manifests").mkdir(exist_ok=True)
    
    def _load_archive_records(self):
        """Load archive records from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM archive_records")
            rows = cursor.fetchall()
            
            for row in rows:
                record = ArchiveRecord(
                    archive_id=row[0],
                    original_path=row[1],
                    archive_path=row[2],
                    archived_at=datetime.fromisoformat(row[3]),
                    risk_level=RiskLevel(row[4]),
                    risk_score=row[5],
                    file_size_mb=row[6],
                    status=ArchiveStatus(row[7]),
                    expires_at=datetime.fromisoformat(row[8]) if row[8] else None,
                    restored_at=datetime.fromisoformat(row[9]) if row[9] else None,
                    metadata=json.loads(row[10]) if row[10] else {}
                )
                self.archive_records.append(record)
            
            conn.close()
            logger.info(f"Loaded {len(self.archive_records)} archive records")
            
        except Exception as e:
            logger.error(f"Error loading archive records: {e}")
    
    async def assess_file_risks(self) -> List[FileRiskAssessment]:
        """Assess risks for all files in workspace"""
        logger.info("🔍 Assessing file risks...")
        
        try:
            risk_assessments = []
            
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    try:
                        assessment = await self._assess_single_file(file_path)
                        if assessment:
                            risk_assessments.append(assessment)
                    except Exception as e:
                        logger.warning(f"Could not assess {file_path}: {e}")
            
            # Sort by risk score (highest first)
            risk_assessments.sort(key=lambda x: x.risk_score, reverse=True)
            
            logger.info(f"✅ Assessed risks for {len(risk_assessments)} files")
            return risk_assessments
            
        except Exception as e:
            logger.error(f"Error assessing file risks: {e}")
            return []
    
    async def _assess_single_file(self, file_path: Path) -> Optional[FileRiskAssessment]:
        """Assess risk for a single file"""
        try:
            relative_path = str(file_path.relative_to(self.base_path))
            stat_info = file_path.stat()
            
            # Basic file information
            size_mb = stat_info.st_size / (1024 * 1024)
            last_accessed = datetime.fromtimestamp(stat_info.st_atime)
            
            # Determine file category
            category = self._categorize_file(relative_path)
            
            # Calculate risk factors
            risk_factors = []
            risk_score = 0.0
            
            # Size factor (larger files are riskier to archive)
            if size_mb > 100:
                risk_factors.append("large_file")
                risk_score += 0.3
            elif size_mb > 10:
                risk_factors.append("medium_file")
                risk_score += 0.2
            
            # Age factor (older files are safer to archive)
            days_since_access = (datetime.now() - last_accessed).days
            if days_since_access > 90:
                risk_factors.append("old_file")
                risk_score -= 0.2
            elif days_since_access < 7:
                risk_factors.append("recently_accessed")
                risk_score += 0.3
            
            # Category factor
            category_config = self.risk_config["file_categories"].get(category, {})
            risk_multiplier = category_config.get("risk_multiplier", 0.5)
            risk_score *= risk_multiplier
            
            # Path factor (sensitive paths are riskier)
            sensitive_paths = ["config", "src", "backend", "frontend", "database"]
            if any(sensitive in relative_path.lower() for sensitive in sensitive_paths):
                risk_factors.append("sensitive_path")
                risk_score += 0.2
            
            # Extension factor
            critical_extensions = [".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".yaml", ".yml"]
            if any(relative_path.endswith(ext) for ext in critical_extensions):
                risk_factors.append("critical_extension")
                risk_score += 0.1
            
            # Normalize risk score
            risk_score = max(0.0, min(1.0, risk_score))
            
            # Determine risk level
            if risk_score >= self.risk_config["risk_thresholds"]["critical"]:
                risk_level = RiskLevel.CRITICAL
            elif risk_score >= self.risk_config["risk_thresholds"]["high"]:
                risk_level = RiskLevel.HIGH
            elif risk_score >= self.risk_config["risk_thresholds"]["medium"]:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # Calculate importance score (inverse of risk for archiving)
            importance_score = (1.0 - risk_score) * 100
            
            assessment = FileRiskAssessment(
                path=relative_path,
                size_mb=size_mb,
                risk_level=risk_level,
                risk_score=risk_score,
                risk_factors=risk_factors,
                last_accessed=last_accessed,
                importance_score=importance_score,
                category=category
            )
            
            # Store assessment in database
            await self._store_risk_assessment(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing file {file_path}: {e}")
            return None
    
    def _categorize_file(self, file_path: str) -> str:
        """Categorize file based on path and extension"""
        file_lower = file_path.lower()
        
        if any(pattern in file_lower for pattern in ["log", ".log"]):
            return "logs"
        elif any(pattern in file_lower for pattern in ["temp", "tmp", ".tmp"]):
            return "temp"
        elif any(pattern in file_lower for pattern in ["cache", ".cache"]):
            return "cache"
        elif any(pattern in file_lower for pattern in ["backup", ".bak", ".backup"]):
            return "backup"
        elif any(pattern in file_lower for pattern in ["doc", "readme", ".md"]):
            return "documentation"
        elif any(pattern in file_lower for pattern in [".py", ".ts", ".tsx", ".js", ".jsx"]):
            return "source_code"
        elif any(pattern in file_lower for pattern in [".json", ".yaml", ".yml", ".conf", ".config"]):
            return "configuration"
        else:
            return "other"
    
    async def _store_risk_assessment(self, assessment: FileRiskAssessment):
        """Store risk assessment in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO risk_assessments 
                (file_path, risk_level, risk_score, risk_factors, importance_score, category, last_assessed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment.path,
                assessment.risk_level.value,
                assessment.risk_score,
                json.dumps(assessment.risk_factors),
                assessment.importance_score,
                assessment.category,
                datetime.now().isoformat(),
                json.dumps({"size_mb": assessment.size_mb, "last_accessed": assessment.last_accessed.isoformat()})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing risk assessment: {e}")
    
    async def archive_medium_risk_files(self, max_files: int = 100) -> Dict[str, Any]:
        """Archive medium-risk files to archived_bin folder"""
        logger.info("📦 Archiving medium-risk files...")
        
        try:
            # Get medium-risk files
            assessments = await self.assess_file_risks()
            medium_risk_files = [
                a for a in assessments 
                if a.risk_level == RiskLevel.MEDIUM
            ][:max_files]
            
            if not medium_risk_files:
                logger.info("No medium-risk files found to archive")
                return {"files_archived": 0, "space_archived_mb": 0}
            
            # Create archive session
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_session = self.archived_bin / "medium_risk" / f"session_{timestamp}"
            archive_session.mkdir(parents=True, exist_ok=True)
            
            archived_files = []
            total_space_archived = 0
            
            for assessment in medium_risk_files:
                try:
                    original_path = self.base_path / assessment.path
                    if not original_path.exists():
                        continue
                    
                    # Create archive path maintaining directory structure
                    archive_path = archive_session / assessment.path
                    archive_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Move file to archive
                    shutil.move(str(original_path), str(archive_path))
                    
                    # Create archive record
                    archive_id = self._generate_archive_id(assessment.path, timestamp)
                    archive_record = ArchiveRecord(
                        archive_id=archive_id,
                        original_path=assessment.path,
                        archive_path=str(archive_path.relative_to(self.base_path)),
                        archived_at=datetime.now(),
                        risk_level=assessment.risk_level,
                        risk_score=assessment.risk_score,
                        file_size_mb=assessment.size_mb,
                        status=ArchiveStatus.ACTIVE,
                        expires_at=datetime.now() + timedelta(days=30),  # 30-day retention
                        metadata={
                            "category": assessment.category,
                            "risk_factors": assessment.risk_factors,
                            "last_accessed": assessment.last_accessed.isoformat()
                        }
                    )
                    
                    # Store archive record
                    await self._store_archive_record(archive_record)
                    self.archive_records.append(archive_record)
                    
                    archived_files.append(assessment.path)
                    total_space_archived += assessment.size_mb
                    
                    logger.info(f"Archived: {assessment.path}")
                    
                except Exception as e:
                    logger.warning(f"Could not archive {assessment.path}: {e}")
            
            # Create archive manifest
            manifest = {
                "archive_session": timestamp,
                "archived_at": datetime.now().isoformat(),
                "files_archived": len(archived_files),
                "space_archived_mb": total_space_archived,
                "archive_folder": str(archive_session.relative_to(self.base_path)),
                "files": archived_files,
                "risk_level": "medium",
                "retention_days": 30
            }
            
            manifest_file = archive_session / "archive_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"✅ Archived {len(archived_files)} medium-risk files ({total_space_archived:.1f} MB)")
            
            return {
                "files_archived": len(archived_files),
                "space_archived_mb": total_space_archived,
                "archive_folder": str(archive_session.relative_to(self.base_path)),
                "manifest_file": str(manifest_file.relative_to(self.base_path))
            }
            
        except Exception as e:
            logger.error(f"Error archiving medium-risk files: {e}")
            return {"error": str(e)}
    
    def _generate_archive_id(self, file_path: str, timestamp: str) -> str:
        """Generate unique archive ID"""
        archive_str = f"{file_path}_{timestamp}"
        return hashlib.md5(archive_str.encode()).hexdigest()[:12]
    
    async def _store_archive_record(self, record: ArchiveRecord):
        """Store archive record in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO archive_records 
                (archive_id, original_path, archive_path, archived_at, risk_level, risk_score, 
                 file_size_mb, status, expires_at, restored_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.archive_id,
                record.original_path,
                record.archive_path,
                record.archived_at.isoformat(),
                record.risk_level.value,
                record.risk_score,
                record.file_size_mb,
                record.status.value,
                record.expires_at.isoformat() if record.expires_at else None,
                record.restored_at.isoformat() if record.restored_at else None,
                json.dumps(record.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing archive record: {e}")
    
    async def restore_archived_file(self, archive_id: str) -> Dict[str, Any]:
        """Restore an archived file"""
        logger.info(f"🔄 Restoring archived file: {archive_id}")
        
        try:
            # Find archive record
            record = next((r for r in self.archive_records if r.archive_id == archive_id), None)
            if not record:
                return {"success": False, "error": "Archive record not found"}
            
            if record.status != ArchiveStatus.ACTIVE:
                return {"success": False, "error": "File is not in active archive"}
            
            # Restore file
            archive_path = self.base_path / record.archive_path
            original_path = self.base_path / record.original_path
            
            if not archive_path.exists():
                return {"success": False, "error": "Archive file not found"}
            
            # Create original directory if needed
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Move file back
            shutil.move(str(archive_path), str(original_path))
            
            # Update record
            record.status = ArchiveStatus.RESTORED
            record.restored_at = datetime.now()
            await self._store_archive_record(record)
            
            logger.info(f"✅ Restored: {record.original_path}")
            
            return {
                "success": True,
                "restored_file": record.original_path,
                "restored_at": record.restored_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error restoring archived file: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_expired_archives(self) -> Dict[str, Any]:
        """Clean up expired archives"""
        logger.info("🧹 Cleaning up expired archives...")
        
        try:
            expired_records = [
                r for r in self.archive_records 
                if r.status == ArchiveStatus.ACTIVE and 
                r.expires_at and 
                r.expires_at < datetime.now()
            ]
            
            cleaned_count = 0
            space_freed = 0
            
            for record in expired_records:
                try:
                    archive_path = self.base_path / record.archive_path
                    if archive_path.exists():
                        archive_path.unlink()
                        space_freed += record.file_size_mb
                    
                    # Move to expired folder
                    expired_folder = self.archived_bin / "expired"
                    expired_folder.mkdir(exist_ok=True)
                    
                    # Update record
                    record.status = ArchiveStatus.EXPIRED
                    await self._store_archive_record(record)
                    
                    cleaned_count += 1
                    logger.info(f"Cleaned up expired archive: {record.original_path}")
                    
                except Exception as e:
                    logger.warning(f"Could not clean up {record.original_path}: {e}")
            
            logger.info(f"✅ Cleaned up {cleaned_count} expired archives ({space_freed:.1f} MB)")
            
            return {
                "expired_archives_cleaned": cleaned_count,
                "space_freed_mb": space_freed
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired archives: {e}")
            return {"error": str(e)}
    
    def get_archive_status(self) -> Dict[str, Any]:
        """Get archive system status"""
        return {
            "total_archives": len(self.archive_records),
            "active_archives": len([r for r in self.archive_records if r.status == ArchiveStatus.ACTIVE]),
            "expired_archives": len([r for r in self.archive_records if r.status == ArchiveStatus.EXPIRED]),
            "restored_archives": len([r for r in self.archive_records if r.status == ArchiveStatus.RESTORED]),
            "total_space_archived_mb": sum(r.file_size_mb for r in self.archive_records if r.status == ArchiveStatus.ACTIVE),
            "archive_folders": {
                "medium_risk": len(list((self.archived_bin / "medium_risk").glob("*"))),
                "high_risk": len(list((self.archived_bin / "high_risk").glob("*"))),
                "expired": len(list((self.archived_bin / "expired").glob("*")))
            }
        }
    
    async def generate_archive_report(self) -> Dict[str, Any]:
        """Generate comprehensive archive report"""
        logger.info("📊 Generating archive report...")
        
        try:
            status = self.get_archive_status()
            
            # Risk distribution
            risk_distribution = {}
            for record in self.archive_records:
                risk_level = record.risk_level.value
                risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
            
            # Category distribution
            category_distribution = {}
            for record in self.archive_records:
                category = record.metadata.get("category", "unknown")
                category_distribution[category] = category_distribution.get(category, 0) + 1
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "archive_status": status,
                "risk_distribution": risk_distribution,
                "category_distribution": category_distribution,
                "recent_archives": [
                    {
                        "archive_id": r.archive_id,
                        "original_path": r.original_path,
                        "archived_at": r.archived_at.isoformat(),
                        "risk_level": r.risk_level.value,
                        "file_size_mb": r.file_size_mb,
                        "status": r.status.value
                    }
                    for r in sorted(self.archive_records, key=lambda x: x.archived_at, reverse=True)[:10]
                ]
            }
            
            # Save report
            report_file = self.base_path / "archive_report.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"📊 Archive report saved to {report_file}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating archive report: {e}")
            return {"error": str(e)}


# Global risk-based archiving system instance
risk_archiving_system = RiskBasedArchivingSystem()


async def main():
    """Main entry point for testing"""
    try:
        # Assess file risks
        assessments = await risk_archiving_system.assess_file_risks()
        
        # Archive medium-risk files
        archive_result = await risk_archiving_system.archive_medium_risk_files(max_files=50)
        
        # Generate report
        report = await risk_archiving_system.generate_archive_report()
        
        print("📦 RISK-BASED ARCHIVING SYSTEM STATUS")
        print("=" * 50)
        print(f"Files Assessed: {len(assessments)}")
        print(f"Files Archived: {archive_result.get('files_archived', 0)}")
        print(f"Space Archived: {archive_result.get('space_archived_mb', 0):.1f} MB")
        
        status = risk_archiving_system.get_archive_status()
        print(f"Total Archives: {status['total_archives']}")
        print(f"Active Archives: {status['active_archives']}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
