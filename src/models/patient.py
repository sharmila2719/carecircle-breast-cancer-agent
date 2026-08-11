"""
Patient model for CareCircle.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from src.models.database import Base


class Patient(Base):
    """Patient information model."""

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)

    # Risk Assessment Fields
    age = Column(Integer, nullable=False)
    family_history = Column(Boolean, default=False)
    genetic_markers = Column(String(255), nullable=True)  # e.g., BRCA1, BRCA2
    previous_biopsies = Column(Integer, default=0)
    breast_density = Column(String(50), nullable=True)  # fatty, scattered, heterogeneous, dense
    hormone_therapy = Column(Boolean, default=False)
    bmi = Column(Float, nullable=True)
    smoking_history = Column(Boolean, default=False)
    alcohol_consumption = Column(String(50), nullable=True)  # none, light, moderate, heavy

    # Calculated Risk Score (0-100)
    risk_score = Column(Float, nullable=True)
    risk_category = Column(String(50), nullable=True)  # low, moderate, high, very_high

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.first_name} {self.last_name}, risk={self.risk_category})>"
