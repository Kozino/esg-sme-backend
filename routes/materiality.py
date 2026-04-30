from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, ESGData, MaterialityAssessment
from ..schemas import MaterialityResponse
from ..auth import get_current_user

router = APIRouter(prefix="/materiality", tags=["Materiality Assessment"])

@router.post("/assess/{year}", response_model=MaterialityResponse)
def assess_materiality(year: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    esg_data = db.query(ESGData).filter(
        ESGData.user_id == current_user.id,
        ESGData.reporting_year == year
    ).first()
    
    if not esg_data:
        raise HTTPException(status_code=404, detail="No ESG data found")
    
    # Calculate scores based on manual page 8 methodology
    env_score = calculate_env_materiality(esg_data)
    social_score = calculate_social_materiality(esg_data)
    gov_score = calculate_gov_materiality(esg_data)
    
    priority_topics = []
    if env_score > 50:
        priority_topics.extend(["GHG Emissions", "Energy Management", "Waste Management"])
    if social_score > 50:
        priority_topics.extend(["Health & Safety", "Human Capital", "Diversity"])
    if gov_score > 50:
        priority_topics.extend(["Corporate Governance", "Supply Chain", "Data Privacy"])
    
    recommendations = generate_recommendations(env_score, social_score, gov_score, priority_topics)
    
    # Save to database
    assessment = MaterialityAssessment(
        esg_data_id=esg_data.id,
        env_score=env_score,
        social_score=social_score,
        gov_score=gov_score,
        priority_topics=priority_topics,
        recommendations=recommendations
    )
    db.add(assessment)
    db.commit()
    
    return MaterialityResponse(
        env_score=env_score,
        social_score=social_score,
        gov_score=gov_score,
        priority_topics=priority_topics,
        recommendations=recommendations
    )

def calculate_env_materiality(data: ESGData) -> float:
    score = 0
    if data.scope1_emissions > 100:
        score += 30
    elif data.scope1_emissions > 50:
        score += 20
    if data.total_water_consumption > 1000:
        score += 30
    if data.total_waste_generated > 50:
        score += 20
    if data.renewable_energy_percentage < 20:
        score += 20
    return min(score, 100)

def calculate_social_materiality(data: ESGData) -> float:
    score = 0
    if data.total_employees > 100:
        score += 30
    if data.employee_turnover_rate > 20:
        score += 30
    if data.ltifr > 5:
        score += 20
    if data.women_in_board_percentage < 30:
        score += 20
    return min(score, 100)

def calculate_gov_materiality(data: ESGData) -> float:
    score = 0
    if not data.has_antibribery_policy:
        score += 40
    if data.supplier_esg_screened < 50:
        score += 30
    if data.data_breaches_count > 0:
        score += 30
    return min(score, 100)

def generate_recommendations(env, social, gov, topics) -> str:
    recs = []
    if env < 50:
        recs.append("Implement energy efficiency measures and track Scope 1 & 2 emissions quarterly")
    if social < 50:
        recs.append("Develop health & safety training program and diversity inclusion policy")
    if gov < 50:
        recs.append("Establish anti-bribery policy and screen 100% of suppliers for ESG compliance")
    
    if not recs:
        recs.append("Maintain current practices and work towards Advanced KPIs (pages 29-32)")
    
    return " ".join(recs)