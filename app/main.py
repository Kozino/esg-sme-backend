from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import auth, esg_data, reports, materiality

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ESG SME Platform Qatar", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(esg_data.router)
app.include_router(reports.router)
app.include_router(materiality.router)

@app.get("/")
def root():
    return {"message": "ESG SME Platform API - Qatar", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}