"""
Notification model for CareCircle.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from src.models.database import Base


class Notification(Base):
    """Notification records for patient communications."""

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    notification_type = Column(String(50), nullable=False)  # email, sms, in_app
    category = Column(String(100), nullable=False)  # screening_reminder, follow_up, education, care_plan_update
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="pending")  # pending, sent, delivered, failed
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification(id={self.id}, patient={self.patient_id}, type={self.notification_type})>"
