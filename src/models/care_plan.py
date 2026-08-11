"""
Care Plan models for CareCircle.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from src.models.database import Base


class CarePlan(Base):
    """Personalized care plan for a patient."""

    __tablename__ = "care_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    risk_category = Column(String(50), nullable=False)
    screening_frequency = Column(String(100), nullable=False)  # e.g., "annual", "bi-annual", "every 6 months"
    recommended_modalities = Column(Text, nullable=True)  # JSON list of screening types
    lifestyle_recommendations = Column(Text, nullable=True)
    genetic_counseling_recommended = Column(Boolean, default=False)
    clinical_trial_eligible = Column(Boolean, default=False)
    status = Column(String(50), default="active")  # active, completed, revised
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CarePlan(id={self.id}, patient={self.patient_id}, status={self.status})>"


class CareTask(Base):
    """Individual tasks within a care plan."""

    __tablename__ = "care_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    care_plan_id = Column(Integer, ForeignKey("care_plans.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(String(100), nullable=False)  # screening, consultation, follow_up, lifestyle, education
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(50), default="medium")  # low, medium, high, urgent
    status = Column(String(50), default="pending")  # pending, in_progress, completed, overdue, cancelled
    assigned_to = Column(String(255), nullable=True)
    completed_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CareTask(id={self.id}, title={self.title}, status={self.status})>"
