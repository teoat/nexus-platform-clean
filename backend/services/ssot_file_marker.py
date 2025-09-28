#!/usr/bin/env python3
"""
NUC SSOT File Marker
Marks files as Single Source of Truth (SSOT) and integrates with file locking system
"""

import asyncio
import json
import logging
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SSOTCategory(Enum):
    """SSOT file categories"""
    CONFIGURATION = "configuration"
    SOURCE_CODE = "source_code"
    DATABASE = "database"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    SECURITY = "security"
    MONITORING = "monitoring"
    INTEGRATION = "integration"


class SSOTPriority(Enum):
    """SSOT priority levels"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class SSOTFile:
    """SSOT file information"""
    path: str
    category: SSOTCategory
    priority: SSOTPriority
    checksum: str
    created_at: datetime
    updated_at: datetime
    locked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class SSOTFileMarker:
    """SSOT File Marker - Marks files as Single Source of Truth"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "ssot_files.db"
        self.ssot_files: Dict[str, SSOTFile] = {}
        
        # SSOT file patterns
        self.ssot_patterns = {
            SSOTCategory.CONFIGURATION: {
                "package.json", "requirements.txt", "docker-compose.yml",
                "*.yaml", "*.yml", "*.json", "*.env*", "*.conf", "*.config",
                "tsconfig.json", "babel.config.js", "jest.config.js"
            },
            SSOTCategory.SOURCE_CODE: {
                "*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.sql",
                "frontend/web/src/**", "backend/**", "nexus/**"
            },
            SSOTCategory.DATABASE: {
                "*.db", "*.sqlite", "*.sql", "database/**"
            },
            SSOTCategory.DOCUMENTATION: {
                "README.md", "*.md", "docs/**", "documentation/**"
            },
            SSOTCategory.DEPLOYMENT: {
                "Dockerfile*", "docker/**", "k8s/**", "nginx/**",
                "deploy*.sh", "*.sh"
            },
            SSOTCategory.SECURITY: {
                "*.key", "*.pem", "*.crt", "ssl/**", "security/**",
                "*.env", "*.env.*"
            },
            SSOTCategory.MONITORING: {
                "monitoring/**", "grafana/**", "prometheus/**",
                "*.monitoring.*", "health_check.*"
            },
            SSOTCategory.INTEGRATION: {
                "integrations/**", "api/**", "services/**",
                "*_integration.*", "*_service.*"
            }
        }
        
        # Initialize database
        self._init_database()
        
        # Statistics
        self.stats = {
            "ssot_files_marked": 0,
            "ssot_files_updated": 0,
            "ssot_files_locked": 0,
            "errors": 0
        }
    
    def _init_database(self):
        """Initialize SSOT files database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ssot_files (
                path TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                checksum TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                locked BOOLEAN DEFAULT FALSE,
                metadata TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def mark_files_as_ssot(self) -> Dict[str, Any]:
        """Mark files as SSOT based on patterns"""
        logger.info("🏷️  Marking files as SSOT...")
        
        try:
            marked_files = []
            
            for category, patterns in self.ssot_patterns.items():
                category_files = await self._find_files_for_category(patterns)
                
                for file_path in category_files:
                    try:
                        ssot_file = await self._create_ssot_file(file_path, category)
                        if ssot_file:
                            self.ssot_files[file_path] = ssot_file
                            await self._store_ssot_file(ssot_file)
                            marked_files.append(file_path)
                            self.stats["ssot_files_marked"] += 1
                            
                    except Exception as e:
                        logger.error(f"Error marking file {file_path} as SSOT: {e}")
                        self.stats["errors"] += 1
            
            logger.info(f"✅ Marked {len(marked_files)} files as SSOT")
            
            return {
                "marked_files": len(marked_files),
                "files_by_category": {
                    category.value: len([f for f in self.ssot_files.values() if f.category == category])
                    for category in SSOTCategory
                },
                "stats": self.stats
            }
            
        except Exception as e:
            logger.error(f"Error marking files as SSOT: {e}")
            self.stats["errors"] += 1
            return {"error": str(e)}
    
    async def _find_files_for_category(self, patterns: Set[str]) -> List[str]:
        """Find files matching category patterns"""
        files = []
        
        for pattern in patterns:
            try:
                if "**" in pattern:
                    # Recursive search
                    for file_path in self.base_path.rglob(pattern.replace("**", "*")):
                        if file_path.is_file():
                            files.append(str(file_path.relative_to(self.base_path)))
                elif "*" in pattern:
                    # Wildcard search
                    for file_path in self.base_path.glob(pattern):
                        if file_path.is_file():
                            files.append(str(file_path.relative_to(self.base_path)))
                else:
                    # Exact match
                    file_path = self.base_path / pattern
                    if file_path.exists() and file_path.is_file():
                        files.append(str(file_path.relative_to(self.base_path)))
                        
            except Exception as e:
                logger.error(f"Error finding files with pattern {pattern}: {e}")
        
        return list(set(files))  # Remove duplicates
    
    async def _create_ssot_file(self, file_path: str, category: SSOTCategory) -> Optional[SSOTFile]:
        """Create SSOT file object"""
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return None
            
            # Calculate checksum
            import hashlib
            checksum = hashlib.md5(full_path.read_bytes()).hexdigest()
            
            # Determine priority based on category
            priority_map = {
                SSOTCategory.CONFIGURATION: SSOTPriority.CRITICAL,
                SSOTCategory.SOURCE_CODE: SSOTPriority.HIGH,
                SSOTCategory.DATABASE: SSOTPriority.CRITICAL,
                SSOTCategory.DOCUMENTATION: SSOTPriority.MEDIUM,
                SSOTCategory.DEPLOYMENT: SSOTPriority.HIGH,
                SSOTCategory.SECURITY: SSOTPriority.CRITICAL,
                SSOTCategory.MONITORING: SSOTPriority.MEDIUM,
                SSOTCategory.INTEGRATION: SSOTPriority.HIGH
            }
            
            priority = priority_map.get(category, SSOTPriority.MEDIUM)
            
            # Get file metadata
            stat_info = full_path.stat()
            metadata = {
                "size": stat_info.st_size,
                "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat_info.st_atime).isoformat()
            }
            
            ssot_file = SSOTFile(
                path=file_path,
                category=category,
                priority=priority,
                checksum=checksum,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata=metadata
            )
            
            return ssot_file
            
        except Exception as e:
            logger.error(f"Error creating SSOT file {file_path}: {e}")
            return None
    
    async def _store_ssot_file(self, ssot_file: SSOTFile):
        """Store SSOT file in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO ssot_files
                (path, category, priority, checksum, created_at, updated_at, locked, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ssot_file.path,
                ssot_file.category.value,
                ssot_file.priority.value,
                ssot_file.checksum,
                ssot_file.created_at.isoformat(),
                ssot_file.updated_at.isoformat(),
                ssot_file.locked,
                json.dumps(ssot_file.metadata)
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing SSOT file {ssot_file.path}: {e}")
    
    async def load_ssot_files(self):
        """Load SSOT files from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM ssot_files")
            rows = cursor.fetchall()
            
            for row in rows:
                path, category, priority, checksum, created_at, updated_at, locked, metadata = row
                
                ssot_file = SSOTFile(
                    path=path,
                    category=SSOTCategory(category),
                    priority=SSOTPriority(priority),
                    checksum=checksum,
                    created_at=datetime.fromisoformat(created_at),
                    updated_at=datetime.fromisoformat(updated_at),
                    locked=bool(locked),
                    metadata=json.loads(metadata) if metadata else {}
                )
                
                self.ssot_files[path] = ssot_file
            
            conn.close()
            logger.info(f"Loaded {len(self.ssot_files)} SSOT files from database")
            
        except Exception as e:
            logger.error(f"Error loading SSOT files: {e}")
    
    async def lock_ssot_files(self):
        """Lock all SSOT files"""
        logger.info("🔒 Locking SSOT files...")
        
        try:
            locked_count = 0
            
            for ssot_file in self.ssot_files.values():
                try:
                    file_path = self.base_path / ssot_file.path
                    
                    if file_path.exists():
                        # Make read-only
                        import stat
                        current_perms = file_path.stat().st_mode
                        file_path.chmod(current_perms & ~stat.S_IWRITE)
                        
                        # Update SSOT file status
                        ssot_file.locked = True
                        ssot_file.updated_at = datetime.now()
                        await self._store_ssot_file(ssot_file)
                        
                        locked_count += 1
                        self.stats["ssot_files_locked"] += 1
                        
                        logger.info(f"🔒 Locked SSOT file: {ssot_file.path}")
                        
                except Exception as e:
                    logger.error(f"Error locking SSOT file {ssot_file.path}: {e}")
                    self.stats["errors"] += 1
            
            logger.info(f"✅ Locked {locked_count} SSOT files")
            
        except Exception as e:
            logger.error(f"Error locking SSOT files: {e}")
            self.stats["errors"] += 1
    
    async def verify_ssot_integrity(self) -> Dict[str, Any]:
        """Verify SSOT file integrity"""
        logger.info("🔍 Verifying SSOT file integrity...")
        
        try:
            verification_results = {
                "total_files": len(self.ssot_files),
                "verified_files": 0,
                "modified_files": 0,
                "missing_files": 0,
                "errors": 0
            }
            
            for ssot_file in self.ssot_files.values():
                try:
                    file_path = self.base_path / ssot_file.path
                    
                    if not file_path.exists():
                        verification_results["missing_files"] += 1
                        logger.warning(f"Missing SSOT file: {ssot_file.path}")
                        continue
                    
                    # Calculate current checksum
                    import hashlib
                    current_checksum = hashlib.md5(file_path.read_bytes()).hexdigest()
                    
                    if current_checksum != ssot_file.checksum:
                        verification_results["modified_files"] += 1
                        logger.warning(f"Modified SSOT file: {ssot_file.path}")
                        
                        # Update checksum
                        ssot_file.checksum = current_checksum
                        ssot_file.updated_at = datetime.now()
                        await self._store_ssot_file(ssot_file)
                        self.stats["ssot_files_updated"] += 1
                    else:
                        verification_results["verified_files"] += 1
                        
                except Exception as e:
                    logger.error(f"Error verifying SSOT file {ssot_file.path}: {e}")
                    verification_results["errors"] += 1
            
            logger.info(f"✅ SSOT integrity verification complete: {verification_results}")
            return verification_results
            
        except Exception as e:
            logger.error(f"Error verifying SSOT integrity: {e}")
            return {"error": str(e)}
    
    def get_ssot_status(self) -> Dict[str, Any]:
        """Get SSOT system status"""
        return {
            "total_ssot_files": len(self.ssot_files),
            "files_by_category": {
                category.value: len([f for f in self.ssot_files.values() if f.category == category])
                for category in SSOTCategory
            },
            "files_by_priority": {
                priority.name: len([f for f in self.ssot_files.values() if f.priority == priority])
                for priority in SSOTPriority
            },
            "locked_files": len([f for f in self.ssot_files.values() if f.locked]),
            "stats": self.stats
        }
    
    def get_ssot_files(self, category: Optional[SSOTCategory] = None, priority: Optional[SSOTPriority] = None) -> List[Dict[str, Any]]:
        """Get SSOT files with optional filtering"""
        files = list(self.ssot_files.values())
        
        if category:
            files = [f for f in files if f.category == category]
        
        if priority:
            files = [f for f in files if f.priority == priority]
        
        return [
            {
                "path": f.path,
                "category": f.category.value,
                "priority": f.priority.name,
                "checksum": f.checksum,
                "created_at": f.created_at.isoformat(),
                "updated_at": f.updated_at.isoformat(),
                "locked": f.locked,
                "metadata": f.metadata
            }
            for f in files
        ]
    
    async def export_ssot_manifest(self, file_path: str):
        """Export SSOT manifest"""
        try:
            manifest = {
                "timestamp": datetime.now().isoformat(),
                "base_path": str(self.base_path),
                "ssot_files": self.get_ssot_files(),
                "status": self.get_ssot_status()
            }
            
            with open(file_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Exported SSOT manifest to {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting SSOT manifest: {e}")


# Global SSOT file marker instance
ssot_file_marker = SSOTFileMarker()


async def main():
    """Main entry point for testing"""
    try:
        # Mark files as SSOT
        result = await ssot_file_marker.mark_files_as_ssot()
        print(f"SSOT Marking Result: {json.dumps(result, indent=2)}")
        
        # Load SSOT files
        await ssot_file_marker.load_ssot_files()
        
        # Lock SSOT files
        await ssot_file_marker.lock_ssot_files()
        
        # Verify integrity
        verification = await ssot_file_marker.verify_ssot_integrity()
        print(f"SSOT Verification: {json.dumps(verification, indent=2)}")
        
        # Get status
        status = ssot_file_marker.get_ssot_status()
        print(f"SSOT Status: {json.dumps(status, indent=2)}")
        
        # Export manifest
        await ssot_file_marker.export_ssot_manifest("ssot_manifest.json")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
