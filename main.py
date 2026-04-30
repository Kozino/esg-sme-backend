from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI(title="ESG SME Platform Qatar")

# Allow all CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test endpoint
@app.get("/")
def root():
    return {"message": "ESG API is running!", "status": "active"}

@app.get("/health")
def health():
    return {"status": "healthy"}

# Simple login endpoint for testing
@app.post("/auth/login")
async def login(email: str, password: str):
    return {"access_token": "fake-token-for-testing", "token_type": "bearer"}

# Serve frontend files (if frontend folder exists)
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
    app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = frontend_path / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_path / "index.html")
