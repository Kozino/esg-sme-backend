from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    company_name: str
    sector: str
    num_employees: Optional[int] = 0

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    company_name: str
    sector: str
    num_employees: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ESGDataCreate(BaseModel):
    reporting_year: int
    # Environment
    scope1_emissions: Optional[float] = 0
    scope2_emissions: Optional[float] = 0
    scope3_emissions: Optional[float] = 0
    total_electricity_kwh: Optional[float] = 0
    renewable_energy_percentage: Optional[float] = 0
    total_water_consumption: Optional[float] = 0
    total_waste_generated: Optional[float] = 0
    waste_recycled_percentage: Optional[float] = 0
    # Social
    total_employees: Optional[int] = 0
    employee_turnover_rate: Optional[float] = 0
    ltifr: Optional[float] = 0
    safety_training_completion: Optional[float] = 0
    women_in_board_percentage: Optional[float] = 0
    qatarization_percentage: Optional[float] = 0
    # Governance
    has_antibribery_policy: Optional[bool] = False
    supplier_esg_screened: Optional[float] = 0
    local_procurement_percentage: Optional[float] = 0
    data_breaches_count: Optional[int] = 0

class ESGDataResponse(ESGDataCreate):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class MaterialityResponse(BaseModel):
    env_score: float
    social_score: float
    gov_score: float
    priority_topics: List[str]
    recommendations: str