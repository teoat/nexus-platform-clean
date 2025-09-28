#!/usr/bin/env python3
"""
NEXUS Platform - Project-Trading Intersection Service V3.0
Service for managing project-trading intersections and unified finance dashboard
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from schemas.enhanced_user import ProjectMilestone as ProjectMilestoneSchema
from schemas.enhanced_user import \
    ProjectTradingIntersection as ProjectTradingIntersectionSchema
from schemas.enhanced_user import TradingOperation as TradingOperationSchema
from sqlalchemy.orm import Session

from database.database import get_db
from database.enhanced_models import (Project, ProjectMilestone,
                                      TradingOperation, User)

logger = logging.getLogger(__name__)


class ProjectTradingIntersectionService:
    """Service for managing project-trading intersections and unified finance dashboard"""

    def __init__(self):
        self.intersection_analyzers = self._initialize_intersection_analyzers()

    def _initialize_intersection_analyzers(self) -> Dict[str, Any]:
        """Initialize intersection analysis tools"""
        return {
            "cashflow_analyzer": {
                "name": "Cash Flow Analyzer",
                "description": "Analyze cash flow patterns between projects and trading",
                "category": "financial_analysis",
            },
            "variance_detector": {
                "name": "Variance Detector",
                "description": "Detect variances between planned and actual allocations",
                "category": "variance_analysis",
            },
            "risk_assessor": {
                "name": "Risk Assessor",
                "description": "Assess financial risks in project-trading intersections",
                "category": "risk_analysis",
            },
            "allocation_optimizer": {
                "name": "Allocation Optimizer",
                "description": "Optimize fund allocation between projects and trading",
                "category": "optimization",
            },
        }

    async def create_project(
        self,
        db: Session,
        user_id: int,
        name: str,
        description: str,
        total_budget: float,
        start_date: datetime,
        end_date: Optional[datetime] = None,
    ) -> Project:
        """Create a new project"""
        try:
            project_id = str(uuid.uuid4())

            project = Project(
                id=project_id,
                user_id=user_id,
                name=name,
                description=description,
                total_budget=total_budget,
                start_date=start_date,
                end_date=end_date,
                status="active",
            )

            db.add(project)
            db.commit()
            db.refresh(project)

            return project

        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise

    async def create_milestone(
        self,
        db: Session,
        project_id: str,
        name: str,
        description: str,
        planned_amount: float,
        release_date: datetime,
    ) -> ProjectMilestone:
        """Create a new project milestone"""
        try:
            milestone_id = str(uuid.uuid4())

            milestone = ProjectMilestone(
                id=milestone_id,
                project_id=project_id,
                name=name,
                description=description,
                planned_amount=planned_amount,
                release_date=release_date,
                status="pending",
            )

            db.add(milestone)
            db.commit()
            db.refresh(milestone)

            return milestone

        except Exception as e:
            logger.error(f"Error creating milestone: {e}")
            raise

    async def create_trading_operation(
        self,
        db: Session,
        user_id: int,
        operation_type: str,
        amount: float,
        description: str,
        category: str,
        date: datetime,
        milestone_id: Optional[str] = None,
    ) -> TradingOperation:
        """Create a new trading operation"""
        try:
            operation_id = str(uuid.uuid4())

            operation = TradingOperation(
                id=operation_id,
                user_id=user_id,
                milestone_id=milestone_id,
                type=operation_type,
                amount=amount,
                description=description,
                category=category,
                date=date,
                linked_milestone=milestone_id,
            )

            db.add(operation)
            db.commit()
            db.refresh(operation)

            return operation

        except Exception as e:
            logger.error(f"Error creating trading operation: {e}")
            raise

    async def analyze_intersection(
        self, db: Session, project_id: str, milestone_id: str
    ) -> ProjectTradingIntersectionSchema:
        """Analyze project-trading intersection"""
        try:
            # Get milestone
            milestone = (
                db.query(ProjectMilestone)
                .filter(
                    ProjectMilestone.id == milestone_id,
                    ProjectMilestone.project_id == project_id,
                )
                .first()
            )

            if not milestone:
                raise ValueError("Milestone not found")

            # Get related trading operations
            trading_operations = (
                db.query(TradingOperation)
                .filter(TradingOperation.milestone_id == milestone_id)
                .all()
            )

            # Calculate allocation
            allocation = await self._calculate_allocation(milestone, trading_operations)

            # Perform intersection analysis
            intersection_analysis = await self._perform_intersection_analysis(
                milestone, trading_operations
            )

            # Calculate variance
            variance = await self._calculate_variance(milestone, trading_operations)

            # Assess risk level
            risk_level = await self._assess_risk_level(
                milestone, trading_operations, variance
            )

            return ProjectTradingIntersectionSchema(
                project_id=project_id,
                milestone_id=milestone_id,
                milestone=ProjectMilestoneSchema.from_orm(milestone),
                trading_operations=[
                    TradingOperationSchema.from_orm(op) for op in trading_operations
                ],
                allocation=allocation,
                intersection_analysis=intersection_analysis,
                variance=variance,
                risk_level=risk_level,
            )

        except Exception as e:
            logger.error(f"Error analyzing intersection: {e}")
            raise

    async def _calculate_allocation(
        self, milestone: ProjectMilestone, trading_operations: List[TradingOperation]
    ) -> Dict[str, float]:
        """Calculate fund allocation between project and trading"""
        try:
            total_planned = float(milestone.planned_amount)
            total_actual = (
                float(milestone.actual_amount) if milestone.actual_amount else 0.0
            )

            # Calculate trading income and expenses
            trading_income = sum(
                float(op.amount) for op in trading_operations if op.type == "income"
            )
            trading_expenses = sum(
                float(op.amount) for op in trading_operations if op.type == "expense"
            )
            trading_net = trading_income - trading_expenses

            # Calculate allocation percentages
            project_allocation = (
                (total_actual / total_planned * 100) if total_planned > 0 else 0
            )
            trading_allocation = (
                (trading_net / total_planned * 100) if total_planned > 0 else 0
            )
            remaining_allocation = max(0, 100 - project_allocation - trading_allocation)

            return {
                "project_percentage": round(project_allocation, 2),
                "trading_percentage": round(trading_allocation, 2),
                "remaining_percentage": round(remaining_allocation, 2),
                "project_amount": total_actual,
                "trading_amount": trading_net,
                "remaining_amount": total_planned - total_actual - trading_net,
            }

        except Exception as e:
            logger.error(f"Error calculating allocation: {e}")
            return {}

    async def _perform_intersection_analysis(
        self, milestone: ProjectMilestone, trading_operations: List[TradingOperation]
    ) -> Dict[str, Any]:
        """Perform detailed intersection analysis"""
        try:
            analysis = {
                "milestone_status": milestone.status,
                "funding_efficiency": 0.0,
                "trading_performance": 0.0,
                "timeline_alignment": 0.0,
                "risk_indicators": [],
                "recommendations": [],
            }

            # Calculate funding efficiency
            planned_amount = float(milestone.planned_amount)
            actual_amount = (
                float(milestone.actual_amount) if milestone.actual_amount else 0.0
            )
            analysis["funding_efficiency"] = (
                (actual_amount / planned_amount * 100) if planned_amount > 0 else 0
            )

            # Calculate trading performance
            total_income = sum(
                float(op.amount) for op in trading_operations if op.type == "income"
            )
            total_expenses = sum(
                float(op.amount) for op in trading_operations if op.type == "expense"
            )
            net_trading = total_income - total_expenses
            analysis["trading_performance"] = net_trading

            # Calculate timeline alignment
            current_date = datetime.utcnow()
            milestone_date = milestone.release_date

            if current_date <= milestone_date:
                # Milestone not yet due
                days_remaining = (milestone_date - current_date).days
                analysis["timeline_alignment"] = 100 if days_remaining > 30 else 50
            else:
                # Milestone overdue
                days_overdue = (current_date - milestone_date).days
                analysis["timeline_alignment"] = max(0, 100 - days_overdue * 5)

            # Identify risk indicators
            if analysis["funding_efficiency"] < 50:
                analysis["risk_indicators"].append("Low funding efficiency")

            if analysis["trading_performance"] < 0:
                analysis["risk_indicators"].append("Negative trading performance")

            if analysis["timeline_alignment"] < 50:
                analysis["risk_indicators"].append("Timeline misalignment")

            # Generate recommendations
            if analysis["funding_efficiency"] < 80:
                analysis["recommendations"].append(
                    "Increase project funding allocation"
                )

            if analysis["trading_performance"] < 0:
                analysis["recommendations"].append(
                    "Review trading strategy and reduce expenses"
                )

            if analysis["timeline_alignment"] < 70:
                analysis["recommendations"].append(
                    "Accelerate project timeline or adjust milestones"
                )

            return analysis

        except Exception as e:
            logger.error(f"Error performing intersection analysis: {e}")
            return {}

    async def _calculate_variance(
        self, milestone: ProjectMilestone, trading_operations: List[TradingOperation]
    ) -> float:
        """Calculate variance between planned and actual allocations"""
        try:
            planned_amount = float(milestone.planned_amount)
            actual_amount = (
                float(milestone.actual_amount) if milestone.actual_amount else 0.0
            )

            # Calculate trading variance
            trading_income = sum(
                float(op.amount) for op in trading_operations if op.type == "income"
            )
            trading_expenses = sum(
                float(op.amount) for op in trading_operations if op.type == "expense"
            )
            trading_net = trading_income - trading_expenses

            # Calculate total variance
            total_allocated = actual_amount + trading_net
            variance = (
                ((total_allocated - planned_amount) / planned_amount * 100)
                if planned_amount > 0
                else 0
            )

            return round(variance, 2)

        except Exception as e:
            logger.error(f"Error calculating variance: {e}")
            return 0.0

    async def _assess_risk_level(
        self,
        milestone: ProjectMilestone,
        trading_operations: List[TradingOperation],
        variance: float,
    ) -> str:
        """Assess risk level based on intersection analysis"""
        try:
            risk_score = 0

            # Variance risk
            if abs(variance) > 20:
                risk_score += 3
            elif abs(variance) > 10:
                risk_score += 2
            elif abs(variance) > 5:
                risk_score += 1

            # Timeline risk
            current_date = datetime.utcnow()
            if current_date > milestone.release_date:
                days_overdue = (current_date - milestone.release_date).days
                if days_overdue > 30:
                    risk_score += 3
                elif days_overdue > 14:
                    risk_score += 2
                elif days_overdue > 7:
                    risk_score += 1

            # Trading performance risk
            trading_income = sum(
                float(op.amount) for op in trading_operations if op.type == "income"
            )
            trading_expenses = sum(
                float(op.amount) for op in trading_operations if op.type == "expense"
            )
            trading_net = trading_income - trading_expenses

            if trading_net < 0:
                risk_score += 2
            elif trading_net < planned_amount * 0.1:  # Less than 10% of planned amount
                risk_score += 1

            # Determine risk level
            if risk_score >= 6:
                return "critical"
            elif risk_score >= 4:
                return "high"
            elif risk_score >= 2:
                return "medium"
            else:
                return "low"

        except Exception as e:
            logger.error(f"Error assessing risk level: {e}")
            return "low"

    async def get_unified_finance_dashboard(
        self, db: Session, user_id: int
    ) -> Dict[str, Any]:
        """Get unified finance dashboard data"""
        try:
            # Get all projects for user
            projects = db.query(Project).filter(Project.user_id == user_id).all()

            # Get all milestones
            milestones = []
            for project in projects:
                project_milestones = (
                    db.query(ProjectMilestone)
                    .filter(ProjectMilestone.project_id == project.id)
                    .all()
                )
                milestones.extend(project_milestones)

            # Get all trading operations
            trading_operations = (
                db.query(TradingOperation)
                .filter(TradingOperation.user_id == user_id)
                .all()
            )

            # Calculate dashboard metrics
            total_project_budget = sum(float(p.total_budget) for p in projects)
            total_milestone_releases = sum(
                float(m.actual_amount or 0) for m in milestones
            )
            total_trading_income = sum(
                float(op.amount) for op in trading_operations if op.type == "income"
            )
            total_trading_expenses = sum(
                float(op.amount) for op in trading_operations if op.type == "expense"
            )
            net_trading = total_trading_income - total_trading_expenses

            # Calculate utilization rate
            utilization_rate = (
                ((total_milestone_releases + net_trading) / total_project_budget * 100)
                if total_project_budget > 0
                else 0
            )

            # Get recent activities
            recent_activities = []

            # Add recent milestones
            recent_milestones = (
                db.query(ProjectMilestone)
                .filter(ProjectMilestone.project_id.in_([p.id for p in projects]))
                .order_by(ProjectMilestone.created_at.desc())
                .limit(5)
                .all()
            )

            for milestone in recent_milestones:
                recent_activities.append(
                    {
                        "type": "milestone",
                        "title": milestone.name,
                        "amount": float(milestone.planned_amount),
                        "date": milestone.release_date,
                        "status": milestone.status,
                    }
                )

            # Add recent trading operations
            recent_trades = (
                db.query(TradingOperation)
                .filter(TradingOperation.user_id == user_id)
                .order_by(TradingOperation.date.desc())
                .limit(5)
                .all()
            )

            for trade in recent_trades:
                recent_activities.append(
                    {
                        "type": "trading",
                        "title": trade.description,
                        "amount": float(trade.amount),
                        "date": trade.date,
                        "category": trade.category,
                    }
                )

            # Sort activities by date
            recent_activities.sort(key=lambda x: x["date"], reverse=True)

            return {
                "summary": {
                    "total_project_budget": total_project_budget,
                    "total_milestone_releases": total_milestone_releases,
                    "total_trading_income": total_trading_income,
                    "total_trading_expenses": total_trading_expenses,
                    "net_trading": net_trading,
                    "utilization_rate": round(utilization_rate, 2),
                },
                "projects": [
                    {"id": p.id, "name": p.name, "status": p.status} for p in projects
                ],
                "milestones": [
                    {"id": m.id, "name": m.name, "status": m.status} for m in milestones
                ],
                "recent_activities": recent_activities[:10],
                "risk_alerts": await self._get_risk_alerts(db, user_id),
                "recommendations": await self._get_recommendations(db, user_id),
            }

        except Exception as e:
            logger.error(f"Error getting unified finance dashboard: {e}")
            raise

    async def _get_risk_alerts(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get risk alerts for the user"""
        try:
            alerts = []

            # Check for overdue milestones
            overdue_milestones = (
                db.query(ProjectMilestone)
                .join(Project)
                .filter(
                    Project.user_id == user_id,
                    ProjectMilestone.release_date < datetime.utcnow(),
                    ProjectMilestone.status == "pending",
                )
                .all()
            )

            for milestone in overdue_milestones:
                alerts.append(
                    {
                        "type": "overdue_milestone",
                        "severity": "high",
                        "message": f"Milestone '{milestone.name}' is overdue",
                        "action": "Review and update milestone timeline",
                    }
                )

            # Check for budget overruns
            projects = db.query(Project).filter(Project.user_id == user_id).all()
            for project in projects:
                milestones = (
                    db.query(ProjectMilestone)
                    .filter(ProjectMilestone.project_id == project.id)
                    .all()
                )

                total_planned = sum(float(m.planned_amount) for m in milestones)
                total_actual = sum(float(m.actual_amount or 0) for m in milestones)

                if total_actual > total_planned:
                    alerts.append(
                        {
                            "type": "budget_overrun",
                            "severity": "medium",
                            "message": f"Project '{project.name}' has exceeded budget",
                            "action": "Review project expenses and adjust budget",
                        }
                    )

            return alerts

        except Exception as e:
            logger.error(f"Error getting risk alerts: {e}")
            return []

    async def _get_recommendations(
        self, db: Session, user_id: int
    ) -> List[Dict[str, Any]]:
        """Get recommendations for the user"""
        try:
            recommendations = []

            # Check for unused features
            user = db.query(User).filter(User.id == user_id).first()
            if not user.primary_pov_role:
                recommendations.append(
                    {
                        "type": "pov_configuration",
                        "priority": "high",
                        "message": "Configure your POV role to get specialized tools",
                        "action": "Go to profile settings and select your professional role",
                    }
                )

            # Check for incomplete projects
            incomplete_projects = (
                db.query(Project)
                .filter(
                    Project.user_id == user_id,
                    Project.status == "active",
                    Project.end_date < datetime.utcnow(),
                )
                .all()
            )

            if incomplete_projects:
                recommendations.append(
                    {
                        "type": "project_completion",
                        "priority": "medium",
                        "message": f"You have {len(incomplete_projects)} incomplete projects",
                        "action": "Review and update project status",
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []


# Create service instance
project_trading_intersection_service = ProjectTradingIntersectionService()
