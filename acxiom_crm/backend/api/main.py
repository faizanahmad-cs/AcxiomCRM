from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from acxiom_crm.backend.config import settings
from acxiom_crm.backend.database import engine, Base
from acxiom_crm.backend.seed_data import seed_database
from acxiom_crm.backend.api.auth_routes import router as auth_router
from acxiom_crm.backend.api.customer_routes import router as customer_router
from acxiom_crm.backend.api.lead_routes import router as lead_router
from acxiom_crm.backend.api.opportunity_routes import router as opp_router
from acxiom_crm.backend.api.followup_routes import router as followup_router
from acxiom_crm.backend.api.report_routes import router as report_router
from acxiom_crm.backend.api.audit_routes import router as audit_router

# Initialize tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AcxiomCRM REST API",
    description="Enterprise Role-Based CRM Backend API covering the full Customer-Sales lifecycle: Lead -> Follow-up -> Opportunity -> Customer with strict validation, RBAC, and audit logging.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(customer_router)
app.include_router(lead_router)
app.include_router(opp_router)
app.include_router(followup_router)
app.include_router(report_router)
app.include_router(audit_router)

@app.on_event("startup")
def on_startup():
    # Ensure database is seeded on start
    seed_database()

@app.get("/", tags=["Root"])
def root():
    return {
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "Operational",
        "documentation": "/docs"
    }

@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "healthy"}

# Global Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", []) if loc != "body"])
        errors.append(f"{field}: {err.get('msg')}" if field else err.get("msg"))
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": "; ".join(errors)}
    )
