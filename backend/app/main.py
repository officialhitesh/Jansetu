from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.models.user import User
from app.models.complaint import Complaint          # ensure table is created
from app.routes.auth_routes import router as auth_router
from app.routes.complaint_routes import router as complaint_router

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="JANSETU API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # tighten to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(complaint_router)   # FIX: was missing — /complaints/* was 404


@app.get("/")
def root():
    return {"message": "JANSETU API is running"}
