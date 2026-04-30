from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
import uuid

app = FastAPI(title="ESG SME Platform Qatar")

# CORS configuration - Allow your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://frontend-kappa-drab-75.vercel.app",  # Your frontend URL
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "*"  # Temporary for testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    company_name: str
    sector: str
    num_employees: Optional[int] = 0

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# In-memory storage
users_db = {}
sessions_db = {}

# ============ AUTHENTICATION ENDPOINTS ============

@app.post("/auth/signup")
async def signup(request: SignupRequest):
    """User registration"""
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    users_db[request.email] = {
        "id": user_id,
        "email": request.email,
        "password": request.password,
        "company_name": request.company_name,
        "sector": request.sector,
        "num_employees": request.num_employees,
        "created_at": datetime.now().isoformat()
    }
    
    return {
        "id": user_id,
        "email": request.email,
        "company_name": request.company_name,
        "sector": request.sector,
        "message": "User created successfully"
    }

@app.post("/auth/login")
async def login(request: LoginRequest):
    """User login"""
    user = users_db.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = str(uuid.uuid4())
    sessions_db[token] = user["id"]
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "company_name": user["company_name"],
            "sector": user["sector"]
        }
    }

@app.get("/auth/me")
async def get_current_user(token: str):
    user_id = sessions_db.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    for email, user in users_db.items():
        if user["id"] == user_id:
            return {
                "id": user["id"],
                "email": email,
                "company_name": user["company_name"],
                "sector": user["sector"],
                "num_employees": user["num_employees"]
            }
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/auth/logout")
async def logout(token: str):
    if token in sessions_db:
        del sessions_db[token]
    return {"message": "Logged out successfully"}

# ============ ESG DATA ENDPOINTS ============
esg_data_db = {}

class ESGDataRequest(BaseModel):
    reporting_year: int
    scope1_emissions: Optional[float] = 0
    scope2_emissions: Optional[float] = 0
    scope3_emissions: Optional[float] = 0
    total_electricity_kwh: Optional[float] = 0
    renewable_energy_percentage: Optional[float] = 0
    total_water_consumption: Optional[float] = 0
    total_waste_generated: Optional[float] = 0
    waste_recycled_percentage: Optional[float] = 0
    total_employees: Optional[int] = 0
    employee_turnover_rate: Optional[float] = 0
    ltifr: Optional[float] = 0
    safety_training_completion: Optional[float] = 0
    women_in_board_percentage: Optional[float] = 0
    qatarization_percentage: Optional[float] = 0
    has_antibribery_policy: Optional[bool] = False
    supplier_esg_screened: Optional[float] = 0
    local_procurement_percentage: Optional[float] = 0
    data_breaches_count: Optional[int] = 0

@app.post("/esg/data")
async def save_esg_data(data: ESGDataRequest):
    key = f"year_{data.reporting_year}"
    esg_data_db[key] = data.dict()
    return {"message": "ESG data saved successfully", "id": len(esg_data_db), **data.dict()}

@app.get("/esg/data/{year}")
async def get_esg_data(year: int):
    key = f"year_{year}"
    if key in esg_data_db:
        return esg_data_db[key]
    return {"reporting_year": year, "message": "No data yet"}

@app.get("/esg/score")
async def get_esg_score():
    return {"score": 78.5, "level": "Silver", "environment": 75, "social": 82, "governance": 78}

# ============ REPORT ENDPOINTS ============
reports_db = {}

@app.post("/reports/generate/{year}")
async def generate_report(year: int, report_type: str = "basic"):
    report_id = len(reports_db) + 1
    reports_db[report_id] = {"id": report_id, "year": year, "type": report_type, "created_at": datetime.now().isoformat()}
    return {"message": "Report generated", "filename": f"esg_report_{year}.pdf", "download_url": f"/reports/download/{report_id}"}

@app.get("/reports/history")
async def get_report_history():
    return list(reports_db.values())

@app.get("/reports/download/{report_id}")
async def download_report(report_id: int):
    from fastapi.responses import PlainTextResponse
    report = reports_db.get(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return PlainTextResponse(f"ESG Report {report_id}\nYear: {report['year']}\nType: {report['type']}", media_type="text/plain")

# ============ MATERIALITY ENDPOINTS ============
@app.post("/materiality/assess/{year}")
async def assess_materiality(year: int):
    return {
        "env_score": 65, "social_score": 70, "gov_score": 60,
        "priority_topics": ["GHG Emissions", "Health & Safety", "Corporate Governance"],
        "recommendations": "Focus on energy reduction and diversity initiatives."
    }

# ============ ROOT ============
@app.get("/")
@app.get("/api")
def root():
    return {"message": "ESG API is running!", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}
