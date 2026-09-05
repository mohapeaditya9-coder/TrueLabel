from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.database import engine, Base
from .routers import upload_router, scan_router, reports_router, dashboard_router

# Initialize database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LMPC Compliance Scanner API",
    description="Backend API for Legal Metrology (Packaged Commodities) Rules, 2011 compliance scanning.",
    version="1.0.0",
)

# Configure CORS so Vite/React dev server can call endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload_router)
app.include_router(scan_router)
app.include_router(reports_router)
app.include_router(dashboard_router)


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint to verify backend operational status.
    """
    return {
        "status": "healthy",
        "service": "LMPC Compliance Scanner API",
        "version": "1.0.0",
    }


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to LMPC Compliance Scanner API",
        "health": "/health",
        "docs": "/docs",
    }
