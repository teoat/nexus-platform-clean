#!/usr/bin/env python3
"""
NUC AI-Powered Maintenance System
Uses machine learning and pattern recognition for intelligent workspace management
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import hashlib
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MaintenancePattern:
    """Maintenance pattern learned from historical data"""
    pattern_type: str
    conditions: Dict[str, Any]
    actions: List[str]
    confidence: float
    success_rate: float
    frequency: int
    last_used: Optional[datetime] = None


@dataclass
class MaintenanceRule:
    """AI-generated maintenance rule"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[str]
    priority: str
    confidence: float
    risk_level: str
    created_at: datetime
    last_executed: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0


class AIMaintenanceSystem:
    """AI-Powered Maintenance System for NUC Workspace Management"""
    
    def __init__(self, base_path: str = "/Users/Arief/Desktop/Nexus"):
        self.base_path = Path(base_path)
        self.db_path = self.base_path / "data" / "ai_maintenance.db"
        self.patterns: List[MaintenancePattern] = []
        self.rules: List[MaintenanceRule] = []
        
        # Initialize database
        self._init_database()
        
        # AI Configuration
        self.ai_config = {
            "learning_threshold": 0.7,
            "confidence_threshold": 0.8,
            "pattern_min_frequency": 3,
            "rule_generation_enabled": True,
            "auto_execution_enabled": False,  # Safety first
            "risk_assessment_enabled": True
        }
        
        # Load existing patterns and rules
        self._load_patterns()
        self._load_rules()
    
    def _init_database(self):
        """Initialize AI maintenance database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Maintenance patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                conditions TEXT NOT NULL,
                actions TEXT NOT NULL,
                confidence REAL NOT NULL,
                success_rate REAL NOT NULL,
                frequency INTEGER NOT NULL,
                last_used TEXT,
                created_at TEXT NOT NULL
            )
        """)
        
        # Maintenance rules table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_rules (
                rule_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                conditions TEXT NOT NULL,
                actions TEXT NOT NULL,
                priority TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_executed TEXT,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0
            )
        """)
        
        # Learning data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation_type TEXT NOT NULL,
                conditions TEXT NOT NULL,
                actions TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                impact_score REAL,
                context TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _load_patterns(self):
        """Load maintenance patterns from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM maintenance_patterns")
            rows = cursor.fetchall()
            
            for row in rows:
                pattern = MaintenancePattern(
                    pattern_type=row[1],
                    conditions=json.loads(row[2]),
                    actions=json.loads(row[3]),
                    confidence=row[4],
                    success_rate=row[5],
                    frequency=row[6],
                    last_used=datetime.fromisoformat(row[7]) if row[7] else None
                )
                self.patterns.append(pattern)
            
            conn.close()
            logger.info(f"Loaded {len(self.patterns)} maintenance patterns")
            
        except Exception as e:
            logger.error(f"Error loading patterns: {e}")
    
    def _load_rules(self):
        """Load maintenance rules from database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM maintenance_rules")
            rows = cursor.fetchall()
            
            for row in rows:
                rule = MaintenanceRule(
                    rule_id=row[0],
                    name=row[1],
                    description=row[2],
                    conditions=json.loads(row[3]),
                    actions=json.loads(row[4]),
                    priority=row[5],
                    confidence=row[6],
                    risk_level=row[7],
                    created_at=datetime.fromisoformat(row[8]),
                    last_executed=datetime.fromisoformat(row[9]) if row[9] else None,
                    success_count=row[10],
                    failure_count=row[11]
                )
                self.rules.append(rule)
            
            conn.close()
            logger.info(f"Loaded {len(self.rules)} maintenance rules")
            
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
    
    async def learn_from_operation(self, operation_type: str, conditions: Dict[str, Any], 
                                 actions: List[str], success: bool, impact_score: float = 0.0):
        """Learn from a maintenance operation"""
        logger.info(f"🧠 Learning from {operation_type} operation...")
        
        try:
            # Store learning data
            await self._store_learning_data(operation_type, conditions, actions, success, impact_score)
            
            # Update patterns
            await self._update_patterns(operation_type, conditions, actions, success)
            
            # Generate new rules if conditions are met
            if self.ai_config["rule_generation_enabled"]:
                await self._generate_rules_from_patterns()
            
            logger.info(f"✅ Learned from {operation_type} operation")
            
        except Exception as e:
            logger.error(f"Error learning from operation: {e}")
    
    async def _store_learning_data(self, operation_type: str, conditions: Dict[str, Any], 
                                 actions: List[str], success: bool, impact_score: float):
        """Store learning data in database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO learning_data 
                (timestamp, operation_type, conditions, actions, success, impact_score, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                operation_type,
                json.dumps(conditions),
                json.dumps(actions),
                success,
                impact_score,
                json.dumps({"source": "ai_maintenance_system"})
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing learning data: {e}")
    
    async def _update_patterns(self, operation_type: str, conditions: Dict[str, Any], 
                             actions: List[str], success: bool):
        """Update maintenance patterns based on new data"""
        try:
            # Find existing pattern or create new one
            pattern_found = False
            
            for pattern in self.patterns:
                if (pattern.pattern_type == operation_type and 
                    self._conditions_match(pattern.conditions, conditions)):
                    
                    # Update existing pattern
                    pattern.frequency += 1
                    if success:
                        pattern.success_rate = ((pattern.success_rate * (pattern.frequency - 1)) + 1) / pattern.frequency
                    else:
                        pattern.success_rate = (pattern.success_rate * (pattern.frequency - 1)) / pattern.frequency
                    
                    pattern.last_used = datetime.now()
                    pattern_found = True
                    break
            
            if not pattern_found:
                # Create new pattern
                new_pattern = MaintenancePattern(
                    pattern_type=operation_type,
                    conditions=conditions.copy(),
                    actions=actions.copy(),
                    confidence=0.5,  # Initial confidence
                    success_rate=1.0 if success else 0.0,
                    frequency=1,
                    last_used=datetime.now()
                )
                self.patterns.append(new_pattern)
            
            # Update confidence based on frequency and success rate
            for pattern in self.patterns:
                if pattern.frequency >= self.ai_config["pattern_min_frequency"]:
                    pattern.confidence = min(pattern.success_rate * (pattern.frequency / 10), 1.0)
            
            # Save patterns to database
            await self._save_patterns()
            
        except Exception as e:
            logger.error(f"Error updating patterns: {e}")
    
    def _conditions_match(self, pattern_conditions: Dict[str, Any], 
                         new_conditions: Dict[str, Any]) -> bool:
        """Check if conditions match (simplified matching)"""
        try:
            # Simple matching based on key overlap
            pattern_keys = set(pattern_conditions.keys())
            new_keys = set(new_conditions.keys())
            
            # At least 70% key overlap
            overlap = len(pattern_keys.intersection(new_keys))
            total_keys = len(pattern_keys.union(new_keys))
            
            return overlap / total_keys >= 0.7
            
        except Exception as e:
            logger.error(f"Error matching conditions: {e}")
            return False
    
    async def _generate_rules_from_patterns(self):
        """Generate maintenance rules from learned patterns"""
        logger.info("🤖 Generating AI maintenance rules...")
        
        try:
            for pattern in self.patterns:
                if (pattern.confidence >= self.ai_config["confidence_threshold"] and 
                    pattern.frequency >= self.ai_config["pattern_min_frequency"]):
                    
                    # Check if rule already exists
                    rule_exists = any(rule.conditions == pattern.conditions for rule in self.rules)
                    
                    if not rule_exists:
                        # Generate new rule
                        rule_id = self._generate_rule_id(pattern)
                        
                        new_rule = MaintenanceRule(
                            rule_id=rule_id,
                            name=f"AI Rule: {pattern.pattern_type}",
                            description=f"Auto-generated rule based on {pattern.frequency} successful operations",
                            conditions=pattern.conditions.copy(),
                            actions=pattern.actions.copy(),
                            priority=self._assess_priority(pattern),
                            confidence=pattern.confidence,
                            risk_level=self._assess_risk_level(pattern),
                            created_at=datetime.now()
                        )
                        
                        self.rules.append(new_rule)
                        await self._save_rule(new_rule)
                        
                        logger.info(f"✅ Generated new rule: {new_rule.name}")
            
        except Exception as e:
            logger.error(f"Error generating rules: {e}")
    
    def _generate_rule_id(self, pattern: MaintenancePattern) -> str:
        """Generate unique rule ID"""
        pattern_str = f"{pattern.pattern_type}_{pattern.frequency}_{pattern.confidence}"
        return hashlib.md5(pattern_str.encode()).hexdigest()[:12]
    
    def _assess_priority(self, pattern: MaintenancePattern) -> str:
        """Assess rule priority based on pattern characteristics"""
        if pattern.confidence >= 0.9 and pattern.success_rate >= 0.9:
            return "high"
        elif pattern.confidence >= 0.7 and pattern.success_rate >= 0.7:
            return "medium"
        else:
            return "low"
    
    def _assess_risk_level(self, pattern: MaintenancePattern) -> str:
        """Assess risk level of rule execution"""
        # Analyze actions for risk
        high_risk_actions = ["delete", "remove", "unlink", "chmod"]
        medium_risk_actions = ["move", "rename", "modify"]
        
        actions_str = " ".join(pattern.actions).lower()
        
        if any(action in actions_str for action in high_risk_actions):
            return "high"
        elif any(action in actions_str for action in medium_risk_actions):
            return "medium"
        else:
            return "low"
    
    async def suggest_maintenance_actions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest maintenance actions based on current context"""
        logger.info("💡 Generating AI maintenance suggestions...")
        
        try:
            suggestions = []
            
            # Analyze context against learned patterns
            for pattern in self.patterns:
                if pattern.confidence >= self.ai_config["learning_threshold"]:
                    match_score = self._calculate_context_match(pattern.conditions, context)
                    
                    if match_score >= 0.6:  # 60% match threshold
                        suggestion = {
                            "pattern_id": pattern.pattern_type,
                            "confidence": pattern.confidence,
                            "match_score": match_score,
                            "suggested_actions": pattern.actions,
                            "success_rate": pattern.success_rate,
                            "risk_level": self._assess_risk_level(pattern),
                            "reasoning": f"Based on {pattern.frequency} similar operations with {pattern.success_rate:.1%} success rate"
                        }
                        suggestions.append(suggestion)
            
            # Sort by confidence and match score
            suggestions.sort(key=lambda x: x["confidence"] * x["match_score"], reverse=True)
            
            logger.info(f"✅ Generated {len(suggestions)} maintenance suggestions")
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
    
    def _calculate_context_match(self, pattern_conditions: Dict[str, Any], 
                               context: Dict[str, Any]) -> float:
        """Calculate how well context matches pattern conditions"""
        try:
            if not pattern_conditions or not context:
                return 0.0
            
            matches = 0
            total_conditions = len(pattern_conditions)
            
            for key, expected_value in pattern_conditions.items():
                if key in context:
                    actual_value = context[key]
                    
                    # Simple value matching (can be enhanced)
                    if isinstance(expected_value, str) and isinstance(actual_value, str):
                        if expected_value.lower() in actual_value.lower():
                            matches += 1
                    elif expected_value == actual_value:
                        matches += 1
                    elif isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                        # Range matching for numeric values
                        if abs(expected_value - actual_value) / max(expected_value, actual_value, 1) < 0.2:
                            matches += 1
            
            return matches / total_conditions if total_conditions > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating context match: {e}")
            return 0.0
    
    async def execute_ai_rule(self, rule_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an AI-generated maintenance rule"""
        logger.info(f"🤖 Executing AI rule: {rule_id}")
        
        try:
            # Find the rule
            rule = next((r for r in self.rules if r.rule_id == rule_id), None)
            if not rule:
                return {"success": False, "error": "Rule not found"}
            
            # Check if rule should be executed based on context
            context_match = self._calculate_context_match(rule.conditions, context)
            if context_match < 0.6:
                return {"success": False, "error": "Context doesn't match rule conditions"}
            
            # Execute actions (simplified - in real implementation, would call actual maintenance functions)
            execution_result = {
                "rule_id": rule_id,
                "rule_name": rule.name,
                "actions_executed": rule.actions,
                "context_match": context_match,
                "execution_time": datetime.now().isoformat(),
                "success": True,  # Simplified
                "impact": "simulated"
            }
            
            # Update rule statistics
            rule.last_executed = datetime.now()
            if execution_result["success"]:
                rule.success_count += 1
            else:
                rule.failure_count += 1
            
            await self._save_rule(rule)
            
            logger.info(f"✅ Executed AI rule: {rule.name}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing AI rule: {e}")
            return {"success": False, "error": str(e)}
    
    async def _save_patterns(self):
        """Save patterns to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Clear existing patterns
            cursor.execute("DELETE FROM maintenance_patterns")
            
            # Insert current patterns
            for pattern in self.patterns:
                cursor.execute("""
                    INSERT INTO maintenance_patterns 
                    (pattern_type, conditions, actions, confidence, success_rate, frequency, last_used, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    pattern.pattern_type,
                    json.dumps(pattern.conditions),
                    json.dumps(pattern.actions),
                    pattern.confidence,
                    pattern.success_rate,
                    pattern.frequency,
                    pattern.last_used.isoformat() if pattern.last_used else None,
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving patterns: {e}")
    
    async def _save_rule(self, rule: MaintenanceRule):
        """Save rule to database"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO maintenance_rules 
                (rule_id, name, description, conditions, actions, priority, confidence, risk_level, 
                 created_at, last_executed, success_count, failure_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                rule.rule_id,
                rule.name,
                rule.description,
                json.dumps(rule.conditions),
                json.dumps(rule.actions),
                rule.priority,
                rule.confidence,
                rule.risk_level,
                rule.created_at.isoformat(),
                rule.last_executed.isoformat() if rule.last_executed else None,
                rule.success_count,
                rule.failure_count
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving rule: {e}")
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get AI maintenance system status"""
        return {
            "patterns_learned": len(self.patterns),
            "rules_generated": len(self.rules),
            "high_confidence_patterns": len([p for p in self.patterns if p.confidence >= 0.8]),
            "active_rules": len([r for r in self.rules if r.confidence >= 0.7]),
            "learning_enabled": self.ai_config["rule_generation_enabled"],
            "auto_execution_enabled": self.ai_config["auto_execution_enabled"],
            "total_learning_operations": len(self.patterns) * 10  # Simplified
        }


# Global AI maintenance system instance
ai_maintenance_system = AIMaintenanceSystem()


async def main():
    """Main entry point for testing"""
    try:
        # Simulate learning from operations
        await ai_maintenance_system.learn_from_operation(
            operation_type="cleanup",
            conditions={"file_count": 1000, "space_used_mb": 500},
            actions=["remove_temp_files", "clean_logs"],
            success=True,
            impact_score=0.8
        )
        
        # Generate suggestions
        context = {"file_count": 1200, "space_used_mb": 600}
        suggestions = await ai_maintenance_system.suggest_maintenance_actions(context)
        
        print("🤖 AI MAINTENANCE SYSTEM STATUS")
        print("=" * 40)
        status = ai_maintenance_system.get_ai_status()
        print(f"Patterns Learned: {status['patterns_learned']}")
        print(f"Rules Generated: {status['rules_generated']}")
        print(f"Suggestions Generated: {len(suggestions)}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")


if __name__ == "__main__":
    asyncio.run(main())
