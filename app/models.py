from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    num_employees = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    esg_data = relationship("ESGData", back_populates="user")
    reports = relationship("Report", back_populates="user")

class ESGData(Base):
    __tablename__ = "esg_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reporting_year = Column(Integer, nullable=False)
    
    # Environment KPIs (Page 16-19)
    scope1_emissions = Column(Float, default=0.0)  # tCO2e
    scope2_emissions = Column(Float, default=0.0)  # tCO2e
    scope3_emissions = Column(Float, default=0.0)  # tCO2e
    total_electricity_kwh = Column(Float, default=0.0)  # kWh
    renewable_energy_percentage = Column(Float, default=0.0)
    total_water_consumption = Column(Float, default=0.0)  # cubic meters
    total_waste_generated = Column(Float, default=0.0)  # tonnes
    waste_recycled_percentage = Column(Float, default=0.0)
    
    # Social KPIs (Page 20-23)
    total_employees = Column(Integer, default=0)
    employee_turnover_rate = Column(Float, default=0.0)
    ltifr = Column(Float, default=0.0)  # Lost Time Injury Frequency Rate
    safety_training_completion = Column(Float, default=0.0)
    women_in_board_percentage = Column(Float, default=0.0)
    qatarization_percentage = Column(Float, default=0.0)
    
    # Governance KPIs (Page 24-27)
    has_antibribery_policy = Column(Boolean, default=False)
    supplier_esg_screened = Column(Float, default=0.0)  # percentage
    local_procurement_percentage = Column(Float, default=0.0)
    data_breaches_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="esg_data")
    materiality = relationship("MaterialityAssessment", back_populates="esg_data", uselist=False)

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    report_type = Column(String, nullable=False)  # basic, advanced, sector
    report_data = Column(JSON, nullable=False)
    pdf_path = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="reports")

class MaterialityAssessment(Base):
    __tablename__ = "materiality_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    esg_data_id = Column(Integer, ForeignKey("esg_data.id"), nullable=False)
    env_score = Column(Float, default=0.0)
    social_score = Column(Float, default=0.0)
    gov_score = Column(Float, default=0.0)
    priority_topics = Column(JSON, default=list)
    recommendations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    esg_data = relationship("ESGData", back_populates="materiality")