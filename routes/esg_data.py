from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import User, ESGData
from ..schemas import ESGDataCreate, ESGDataResponse
from ..auth import get_current_user

router = APIRouter(prefix="/esg", tags=["ESG Data"])

@router.post("/data", response_model=ESGDataResponse)
def save_esg_data(data: ESGDataCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if data for this year already exists
    existing = db.query(ESGData).filter(
        ESGData.user_id == current_user.id,
        ESGData.reporting_year == data.reporting_year
    ).first()
    
    if existing:
        # Update existing
        for key, value in data.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Create new
        new_data = ESGData(**data.dict(), user_id=current_user.id)
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        return new_data

@router.get("/data/{year}", response_model=ESGDataResponse)
def get_esg_data(year: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = db.query(ESGData).filter(
        ESGData.user_id == current_user.id,
        ESGData.reporting_year == year
    ).first()
    if not data:
        raise HTTPException(status_code=404, detail="No data found for this year")
    return data

@router.get("/data/history", response_model=List[ESGDataResponse])
def get_esg_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = db.query(ESGData).filter(ESGData.user_id == current_user.id).order_by(ESGData.reporting_year.desc()).all()
    return data

@router.get("/score")
def get_esg_score(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    latest_data = db.query(ESGData).filter(ESGData.user_id == current_user.id).order_by(ESGData.reporting_year.desc()).first()
    if not latest_data:
        return {"score": 0, "level": "Not Started"}
    
    # Calculate ESG Score (simple weighted average)
    env_score = calculate_env_score(latest_data)
    social_score = calculate_social_score(latest_data)
    gov_score = calculate_gov_score(latest_data)
    total_score = (env_score + social_score + gov_score) / 3
    
    if total_score >= 80:
        level = "Gold"
    elif total_score >= 60:
        level = "Silver"
    elif total_score >= 40:
        level = "Bronze"
    else:
        level = "Basic"
    
    return {
        "score": round(total_score, 1),
        "level": level,
        "environment": round(env_score, 1),
        "social": round(social_score, 1),
        "governance": round(gov_score, 1)
    }

def calculate_env_score(data: ESGData) -> float:
    score = 0
    if data.scope1_emissions > 0 or data.scope2_emissions > 0:
        score += 20
    if data.renewable_energy_percentage > 0:
        score += min(data.renewable_energy_percentage / 10, 20)
    if data.waste_recycled_percentage > 0:
        score += min(data.waste_recycled_percentage / 5, 20)
    if data.total_water_consumption == 0:
        score += 20
    return min(score, 100)

def calculate_social_score(data: ESGData) -> float:
    score = 0
    if data.safety_training_completion > 80:
        score += 25
    elif data.safety_training_completion > 50:
        score += 15
    if data.women_in_board_percentage > 0:
        score += min(data.women_in_board_percentage * 2, 25)
    if data.qatarization_percentage > 0:
        score += min(data.qatarization_percentage, 25)
    if data.employee_turnover_rate < 15:
        score += 25
    elif data.employee_turnover_rate < 30:
        score += 15
    return min(score, 100)

def calculate_gov_score(data: ESGData) -> float:
    score = 0
    if data.has_antibribery_policy:
        score += 25
    if data.supplier_esg_screened > 75:
        score += 25
    elif data.supplier_esg_screened > 50:
        score += 15
    if data.local_procurement_percentage > 50:
        score += 25
    elif data.local_procurement_percentage > 25:
        score += 15
    if data.data_breaches_count == 0:
        score += 25
    return min(score, 100)