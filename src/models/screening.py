"""
Screening models for CareCircle.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from src.models.database import Base


class ScreeningRecord(Base):
    """Record of completed screenings."""

    __tablename__ = "screening_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    screening_type = Column(String(100), nullable=False)  # mammogram, MRI, ultrasound, clinical_exam
    screening_date = Column(DateTime, nullable=False)
    facility = Column(String(255), nullable=True)
    provider = Column(String(255), nullable=True)
    result = Column(String(50), nullable=True)  # normal, abnormal, inconclusive
    birads_score = Column(Integer, nullable=True)  # BI-RADS 0-6
    notes = Column(Text, nullable=True)
    follow_up_required = Column(Boolean, default=False)
    follow_up_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ScreeningRecord(id={self.id}, patient={self.patient_id}, type={self.screening_type})>"


class ScreeningSchedule(Base):
    """Scheduled future screenings."""

    __tablename__ = "screening_schedules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    screening_type = Column(String(100), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    facility = Column(String(255), nullable=True)
    provider = Column(String(255), nullable=True)
    status = Column(String(50), default="scheduled")  # scheduled, confirmed, completed, cancelled, missed
    reminder_sent = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ScreeningSchedule(id={self.id}, patient={self.patient_id}, date={self.scheduled_date})>"
